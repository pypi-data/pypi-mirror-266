locals {
  project = yamldecode(file(var.project_file))
  landscape = yamldecode(file(var.landscape_file))
  applications = yamldecode(file(var.applications_file))
  settings = lookup(local.landscape, "settings", {})
  cosmos_name = local.settings["cosmos_name"]
  realm_name = local.settings["realm_name"]
  foundation_name = local.settings["foundation_name"]
  tf_bucket_name = lookup(local.settings, "cosmos_name")
  folder_id = lookup(local.project, "folder_id", null)
  project_prefix = local.project["project_prefix"]
  billing_account = local.project["billing_account"]
  environment_dict = local.landscape["environments"]
  activated_apps = lookup(lookup(local.landscape["modules"], "gcp-module-project", {}), "applications", [])
}

locals {
  filtered_applications = { for app_name, app in local.applications : app_name => app if contains(local.activated_apps, app_name) }

  all_pool_settings = toset(flatten([
    for app_name, app in local.filtered_applications : [
      for env_name, env in local.environment_dict : {
        app_name          = app_name
        env_name          = env_name
        repository_owner  = app["repository_owner"]
        repository_name   = app["repository_name"]
        project_id        = "${local.project_prefix}${env_name}"
        match_branch      = env["match_branch"]
        match_event       = lookup(env, "match_event", "push")
      }
    ]
  ]))
}

resource "google_storage_bucket_iam_member" "tfstate_bucket_modify" {
  for_each = { for s in local.all_pool_settings : "${s.app_name}-${s.env_name}" => s }
  bucket = local.tf_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.github_provider_sa_dict[each.key].email}"

  condition {
    title       = "PrefixCondition"
    description = "Grants access to objects in a specific directory"
    expression  = "resource.name.startsWith('projects/_/buckets/${local.tf_bucket_name}/objects/${local.realm_name}/_/${local.foundation_name}/${each.value["app_name"]}/${each.value["env_name"]}/')"
  }
}
