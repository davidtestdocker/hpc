# 變數或輸出的用途說明，供工具與操作者閱讀。
# Terraform network：輸出資源屬性，供操作者或其他模組引用；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 公開運算結果；value 可引用資源屬性或模組輸出。
output "network_id" {
  description = "VPC network ID"
  value       = google_compute_network.this.id
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.this.name
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "network_self_link" {
  description = "VPC network self link"
  value       = google_compute_network.this.self_link
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "subnet_id" {
  description = "Subnet ID"
  value       = google_compute_subnetwork.this.id
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "subnet_name" {
  description = "Subnet name"
  value       = google_compute_subnetwork.this.name
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "subnet_self_link" {
  description = "Subnet self link"
  value       = google_compute_subnetwork.this.self_link
}
