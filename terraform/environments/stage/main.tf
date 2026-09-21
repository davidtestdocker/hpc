# 防火牆規則的來源 CIDR 範圍。
# Compute Engine 機型，決定 CPU 與記憶體規格。
# Terraform stage：宣告資源與模組，引用其他資源的屬性建立依賴；現有環境定義不代表已與 gpu-sg 主展示對齊。
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
module "api" {
  source = "../../modules/compute"

  name         = "hpc-api-${var.environment}"
  machine_type = "e2-medium"
  zone         = var.zone
  image        = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"

  network    = module.network.network_id
  subnetwork = module.network.subnet_id
}
