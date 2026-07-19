terraform {
  required_providers {

    google = {

      source = "hashicorp/google"

      version = "~> 7.0"

    }

  }

}

provider "google" {

  project = "YOUR_PROJECT_ID"

  region  = "asia-east1"

  zone    = "asia-east1-a"

}
