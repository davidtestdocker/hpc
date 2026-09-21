# Terraform dev：設定雲端 provider 及其認證／專案環境；現有環境定義不代表已與 gpu-sg 主展示對齊。
# HCL 語法：區塊以 {} 包住，= 指派屬性；var.xxx 讀輸入，module.xxx 讀模組輸出。
# 設定 Terraform 執行需求及 provider 來源／版本。
terraform {
  required_providers {

    google = {

      source = "hashicorp/google"

      version = "~> 7.0"

    }

  }

}

# 設定雲端 API 提供者，例如專案與區域。
provider "google" {

  project = var.project_id

  region = var.region

  zone = var.zone

}
