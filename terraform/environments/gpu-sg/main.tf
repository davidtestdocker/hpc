# default VPC／subnet 是專案共享資源；只以 data source 讀取，避免本環境接管或刪除它們。
data "google_compute_network" "selected" {
  name    = var.network_name
  project = var.project_id
}

data "google_compute_subnetwork" "selected" {
  name    = var.subnetwork_name
  project = var.project_id
  region  = var.region
}

resource "google_container_cluster" "this" {
  name     = var.cluster_name
  project  = var.project_id
  location = var.zone

  # 使用名稱交給 provider 正規化，與既有叢集匯入 state 的表示一致。
  network    = var.network_name
  subnetwork = var.subnetwork_name

  # GKE 建立暫時 default pool 後立即移除；正式 pools 由下方獨立資源管理。
  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = var.deletion_protection

  release_channel {
    channel = "REGULAR"
  }

  networking_mode = "VPC_NATIVE"

  # 空 block 讓 GKE 在既有 subnet 上配置 alias IP ranges。
  # 匯入現有 hpc-gpu-sg 時，provider 會從 state 保留實際 range 名稱。
  ip_allocation_policy {}

  # 對應現有叢集：Shielded Nodes、NodeLocal DNS 與 PD CSI driver。
  enable_shielded_nodes = true

  addons_config {
    dns_cache_config {
      enabled = true
    }

    gce_persistent_disk_csi_driver_config {
      enabled = true
    }

    network_policy_config {
      disabled = !var.enable_network_policy
    }

    node_readiness_config {
      enabled = false
    }
  }

  network_policy {
    enabled  = var.enable_network_policy
    provider = var.enable_network_policy ? "CALICO" : "PROVIDER_UNSPECIFIED"
  }

  lifecycle {
    # 匯入時 API 會回報 initial_node_count=0；它只用於建立暫時的 default pool。
    # 忽略這個 ForceNew 欄位可避免 Terraform 誤判整個現有叢集需要重建。
    ignore_changes = [initial_node_count, min_master_version, remove_default_node_pool]
  }
}

locals {
  # 與現有 GKE Standard node pools 相同的最小 OAuth scopes。
  node_oauth_scopes = [
    "https://www.googleapis.com/auth/devstorage.read_only",
    "https://www.googleapis.com/auth/logging.write",
    "https://www.googleapis.com/auth/monitoring",
    "https://www.googleapis.com/auth/service.management.readonly",
    "https://www.googleapis.com/auth/servicecontrol",
    "https://www.googleapis.com/auth/trace.append",
  ]
}

resource "google_container_node_pool" "system" {
  name     = "system-pool"
  project  = var.project_id
  location = var.zone
  cluster  = google_container_cluster.this.name

  node_count = var.system_node_count

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    strategy  = "SURGE"
    max_surge = 1
  }

  node_config {
    machine_type = "e2-standard-2"
    disk_type    = "pd-balanced"
    disk_size_gb = 30
    image_type   = "COS_CONTAINERD"
    oauth_scopes = local.node_oauth_scopes

    metadata = {
      disable-legacy-endpoints = "true"
    }

    shielded_instance_config {
      enable_integrity_monitoring = true
    }
  }
}

resource "google_container_node_pool" "gpu" {
  name     = "gpu-pool"
  project  = var.project_id
  location = var.zone
  cluster  = google_container_cluster.this.name

  node_count = var.gpu_node_count

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  upgrade_settings {
    strategy        = "SURGE"
    max_unavailable = 1
  }

  node_config {
    machine_type = "g2-standard-4"
    # 主環境預設使用一般 VM；隔離驗收可改用 Spot 配額並接受隨時被回收。
    spot         = var.gpu_spot
    disk_type    = "pd-balanced"
    disk_size_gb = 100
    image_type   = "COS_CONTAINERD"
    oauth_scopes = local.node_oauth_scopes

    metadata = {
      disable-legacy-endpoints = "true"
    }

    guest_accelerator {
      type  = "nvidia-l4"
      count = 1

      gpu_driver_installation_config {
        gpu_driver_version = "DEFAULT"
      }

      gpu_sharing_config {
        gpu_sharing_strategy       = "TIME_SHARING"
        max_shared_clients_per_gpu = 4
      }
    }

    # GKE 會在同時存在 CPU pool 時自動加入 nvidia.com/gpu=present:NoSchedule，
    # 並透過 effective_taints 回報；重複宣告 taint 會造成無效的匯入後 drift。

    shielded_instance_config {
      enable_integrity_monitoring = true
    }
  }
}
