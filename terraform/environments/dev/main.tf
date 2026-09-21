# 防火牆規則的來源 CIDR 範圍。
# 此 node pool 的節點數。
# Compute Engine 機型，決定 CPU 與記憶體規格。
# Terraform dev：宣告資源與模組，引用其他資源的屬性建立依賴；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 呼叫可重用模組；source 指向模組位置，其餘參數對應模組輸入。
module "network" {
  source = "../../modules/network"

  network_name = "hpc-${var.environment}-vpc"
  subnet_name  = "hpc-${var.environment}-subnet"
  subnet_cidr  = var.subnet_cidr
  region       = var.region
}

# 呼叫可重用模組；source 指向模組位置，其餘參數對應模組輸入。
module "firewall" {
  source = "../../modules/firewall"

  firewall_name = "hpc-${var.environment}-firewall"
  network       = module.network.network_self_link

  source_ranges = [
    "0.0.0.0/0"
  ]
}


# 呼叫可重用模組；source 指向模組位置，其餘參數對應模組輸入。
module "gke" {

  source       = "../../modules/gke"
  project_id   = var.project_id
  region       = var.region
  zone         = var.zone
  cluster_name = "hpc-dev"
  network      = module.network.network_name
  subnetwork   = module.network.subnet_name
  node_count   = 1
  machine_type = "e2-standard-2"
}
