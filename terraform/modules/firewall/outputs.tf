# Terraform firewall：輸出資源屬性，供操作者或其他模組引用；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 公開運算結果；value 可引用資源屬性或模組輸出。
output "firewall_name" {
  value = google_compute_firewall.this.name
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "firewall_id" {
  value = google_compute_firewall.this.id
}
