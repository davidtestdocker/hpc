# 是否自動建立各區域的子網路；false 使用自訂子網路。
# 子網路的 IPv4 CIDR 範圍。
# Terraform network：宣告資源與模組，引用其他資源的屬性建立依賴；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 宣告受 Terraform 管理的資源；第一個標籤是類型，第二個是本地名稱。
resource "google_compute_network" "this" {
  name                    = var.network_name
  auto_create_subnetworks = false
}

# 宣告受 Terraform 管理的資源；第一個標籤是類型，第二個是本地名稱。
resource "google_compute_subnetwork" "this" {
  name          = var.subnet_name
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = google_compute_network.this.id
}
