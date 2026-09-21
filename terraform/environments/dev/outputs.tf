# Terraform dev：輸出資源屬性，供操作者或其他模組引用；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 公開運算結果；value 可引用資源屬性或模組輸出。
output "gke_cluster_name" {
  value = module.gke.cluster_name
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "gke_cluster_endpoint" {
  value = module.gke.cluster_endpoint
}
