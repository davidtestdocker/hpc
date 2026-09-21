# 變數或輸出的用途說明，供工具與操作者閱讀。
# Terraform compute：宣告可傳入的變數、型別及預設值；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "name" {
  description = "Compute instance name"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "machine_type" {
  description = "Compute instance machine type"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "zone" {
  description = "Compute instance zone"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "image" {
  description = "Boot disk image"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "network" {
  description = "VPC network name or self link"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "subnetwork" {
  description = "Subnet ID or self link"
  type        = string
}
