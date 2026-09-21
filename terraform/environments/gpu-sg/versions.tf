# 主展示環境使用獨立 Terraform root module，不共用舊 dev state。
terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
  }
}
