resource "google_container_cluster" "this" {

  name     = var.cluster_name
  location = var.zone

  project = var.project_id

  network    = var.network
  subnetwork = var.subnetwork

  deletion_protection = false

  initial_node_count = 1

  remove_default_node_pool = true
}

resource "google_container_node_pool" "primary" {

  name     = "primary-pool"
  project  = var.project_id
  location = var.zone

  cluster = google_container_cluster.this.name

  node_count = var.node_count

  node_config {

    machine_type = var.machine_type

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
