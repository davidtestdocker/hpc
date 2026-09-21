# 防火牆規則的來源 CIDR 範圍。
# Terraform firewall：宣告資源與模組，引用其他資源的屬性建立依賴；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 宣告受 Terraform 管理的資源；第一個標籤是類型，第二個是本地名稱。
resource "google_compute_firewall" "this" {
  name    = var.firewall_name
  network = var.network

  allow {
    protocol = "tcp"

    ports = [
      "22",
      "8000"
    ]
  }

  source_ranges = var.source_ranges
}
