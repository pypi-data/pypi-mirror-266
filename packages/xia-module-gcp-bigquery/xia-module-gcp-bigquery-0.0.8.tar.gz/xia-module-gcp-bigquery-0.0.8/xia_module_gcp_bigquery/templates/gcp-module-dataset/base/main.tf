module "gcp_module_dataset" {
  source = "../../modules/gcp-module-dataset"

  content = "../../content/datasets.yaml"
}
