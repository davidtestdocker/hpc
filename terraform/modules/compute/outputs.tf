# 變數或輸出的用途說明，供工具與操作者閱讀。
# Terraform compute：輸出資源屬性，供操作者或其他模組引用；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 公開運算結果；value 可引用資源屬性或模組輸出。
output "name" {
  description = "Compute instance name"
  value       = google_compute_instance.this.name
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "zone" {
  description = "Compute instance zone"
  value       = google_compute_instance.this.zone
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "internal_ip" {
  description = "Compute instance internal IP"
  value       = google_compute_instance.this.network_interface[0].network_ip
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "machine_type" {
  description = "Compute instance machine type"
  value       = google_compute_instance.this.machine_type
}
