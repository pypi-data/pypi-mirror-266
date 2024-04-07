locals {
  contents         = yamldecode(file(var.content))
}

resource "google_bigquery_dataset" "app_datasets" {
  dataset_id          = local.contents.dataset_id
  description         = local.contents.description
  friendly_name       = local.contents.friendly_name
  location            = local.contents.location
  delete_contents_on_destroy = local.contents.delete_contents_on_destroy
}
