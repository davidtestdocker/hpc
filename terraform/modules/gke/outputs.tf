# 標記敏感輸出以減少 CLI 顯示；不等於加密 state。
# Terraform gke：輸出資源屬性，供操作者或其他模組引用；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 公開運算結果；value 可引用資源屬性或模組輸出。
output "cluster_name" {
  value = google_container_cluster.this.name
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "cluster_endpoint" {
  value = google_container_cluster.this.endpoint
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "cluster_ca_certificate" {
  value     = google_container_cluster.this.master_auth[0].cluster_ca_certificate
  sensitive = true
}
