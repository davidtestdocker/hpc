# 變數或輸出的用途說明，供工具與操作者閱讀。
# Terraform prod：輸出資源屬性，供操作者或其他模組引用；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 公開運算結果；value 可引用資源屬性或模組輸出。
output "vm_name" {
  description = "VM Name"
  value       = module.api.name
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "vm_zone" {
  description = "VM Zone"
  value       = module.api.zone
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "vm_internal_ip" {
  description = "VM internal IP address"
  value       = module.api.internal_ip
}

# 公開運算結果；value 可引用資源屬性或模組輸出。
output "vm_machine_type" {
  description = "VM machine type"
  value       = module.api.machine_type
}
