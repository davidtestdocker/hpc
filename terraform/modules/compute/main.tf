# Compute Engine 機型，決定 CPU 與記憶體規格。
# VM 開機磁碟及其初始化設定。
# VM 網路介面，連接指定 VPC／子網路。
# Terraform compute：宣告資源與模組，引用其他資源的屬性建立依賴；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 宣告受 Terraform 管理的資源；第一個標籤是類型，第二個是本地名稱。
resource "google_compute_instance" "this" {

  name         = var.name
  machine_type = var.machine_type
  zone         = var.zone

  allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = var.image
    }
  }

  network_interface {
    network    = var.network
    subnetwork = var.subnetwork
  }

}
