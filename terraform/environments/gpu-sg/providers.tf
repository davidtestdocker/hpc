# 認證沿用 gcloud Application Default Credentials 或 CI 的 Workload Identity。
# 不把 credential JSON 寫入 Terraform 或 repo。
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}
