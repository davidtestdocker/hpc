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

resource "google_container_node_pool" "observability" {

  name     = "observability-pool"
  project  = var.project_id
  location = var.zone

  cluster = google_container_cluster.this.name

  node_count = 1

  node_config {

    machine_type = "e2-standard-2"
    # 設定 Node Label，之後可透過 nodeSelector 指定 Observability 服務
    # (Prometheus、Grafana、Alertmanager) 部署到此 Node Pool
    labels = {
      workload = "observability"
    }

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
