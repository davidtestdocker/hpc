# Terraform prod：限制 Terraform 或 provider 的相容版本；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 設定 Terraform 執行需求及 provider 來源／版本。
terraform {
  required_version = ">= 1.15.0"
}
