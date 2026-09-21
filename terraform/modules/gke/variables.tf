# 變數或輸出的用途說明，供工具與操作者閱讀。
# 呼叫端未提供變數時使用的預設值。
# Terraform gke：宣告可傳入的變數、型別及預設值；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "region" {
  description = "GCP region"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "zone" {
  description = "GCP zone"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "network" {
  description = "VPC network self link or name"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "subnetwork" {
  description = "Subnetwork self link or name"
  type        = string
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "node_count" {
  description = "Initial number of GKE nodes"
  type        = number
  default     = 1
}

# 宣告輸入變數；type 限制型別，default 提供未傳入時的值。
variable "machine_type" {
  description = "GKE node machine type"
  type        = string
  default     = "e2-standard-2"
}
