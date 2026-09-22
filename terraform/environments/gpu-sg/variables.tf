# 本 root 的輸入契約；依序決定專案／位置、共享網路、節點數與保護機制。
# 不要只改 cluster_name 就沿用主環境 state 做 rehearsal；隔離驗收必須隔離 state。
variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region containing the zonal GKE cluster"
  type        = string
  default     = "asia-southeast1"
}

variable "zone" {
  description = "GCP zone containing the GKE cluster and node pools"
  type        = string
  default     = "asia-southeast1-a"
}

variable "cluster_name" {
  description = "GKE cluster name; change this when creating an isolated rehearsal cluster"
  type        = string
  default     = "hpc-gpu-sg"
}

variable "network_name" {
  description = "Existing shared VPC name; this environment reads but does not own it"
  type        = string
  default     = "default"
}

variable "subnetwork_name" {
  description = "Existing subnetwork name; this environment reads but does not own it"
  type        = string
  default     = "default"
}

variable "system_node_count" {
  description = "Fixed number of system-pool nodes for the current demo environment"
  type        = number
  default     = 1

  validation {
    condition     = var.system_node_count >= 1
    error_message = "system_node_count must be at least one."
  }
}

# CPU-only rehearsal 設 0；此設定不表示有額外 GPU 配額可用。
variable "gpu_node_count" {
  description = "Fixed number of L4 nodes; keep zero only for a CPU-only rehearsal"
  type        = number
  default     = 1

  validation {
    condition     = var.gpu_node_count >= 0
    error_message = "gpu_node_count cannot be negative."
  }
}

variable "gpu_spot" {
  description = "Use Spot VMs for an isolated GPU rehearsal; keep false for the main environment"
  type        = bool
  default     = false
}

# 主環境預設保護；不得為了照跑歷史 destroy 指令而關閉。
variable "deletion_protection" {
  description = "Protect the cluster from accidental Terraform deletion"
  type        = bool
  default     = true
}

# 預設 false 對應主環境現況；僅建立 NetworkPolicy 物件不會啟用封包隔離。
variable "enable_network_policy" {
  description = "Enable GKE Calico NetworkPolicy enforcement; use true for isolated validation clusters"
  type        = bool
  default     = false
}
