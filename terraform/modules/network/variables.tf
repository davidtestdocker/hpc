# 變數或輸出的用途說明，供工具與操作者閱讀。
# Terraform network：宣告可傳入的變數、型別及預設值；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "network_name" {
  description = "VPC network name"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "subnet_name" {
  description = "Subnet name"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "subnet_cidr" {
  description = "Subnet IPv4 CIDR range"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "region" {
  description = "Subnet region"
  type        = string
}
