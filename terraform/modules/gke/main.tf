# 是否阻止 Terraform 刪除叢集；false 代表未啟用刪除保護。
# 叢集建立時的初始節點數。
# 建立叢集後移除預設 node pool，改由獨立資源管理。
# 此 node pool 的節點數。
# Compute Engine 機型，決定 CPU 與記憶體規格。
# 節點可申請的 OAuth scope；實際 API 權限仍受 IAM 限制。
# Terraform gke：宣告資源與模組，引用其他資源的屬性建立依賴；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 宣告受 Terraform 管理的資源；第一個標籤是類型，第二個是本地名稱。
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

# 宣告受 Terraform 管理的資源；第一個標籤是類型，第二個是本地名稱。
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

# 宣告受 Terraform 管理的資源；第一個標籤是類型，第二個是本地名稱。
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
