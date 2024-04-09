terraform {
  backend "gcs" {
  }
}

module "gcp_module_dataset" {
  source = "../../modules/module-state-gcs"
}
