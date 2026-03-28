terraform {
  required_version = ">= 1.4.0"

  backend "gcs" {
    bucket = "project-8be6a108-f8c8-4ef9-879-tfstate"
    prefix = "newsgenie/terraform"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone

  add_terraform_attribution_label = false
}
