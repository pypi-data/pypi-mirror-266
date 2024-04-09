module "activate_module_state_gcs" {
  source = "../../modules/activate-module-state-gcs"

  landscape_file = var.landscape_file
  applications_file = var.applications_file
  project_file = var.project_file
  github_provider_sa_dict = module.gcp_module_project.github_provider_sa

  depends_on = [module.gcp_module_project]
}

