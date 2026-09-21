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

variable "deletion_protection" {
  description = "Protect the cluster from accidental Terraform deletion"
  type        = bool
  default     = true
}

variable "enable_network_policy" {
  description = "Enable GKE Calico NetworkPolicy enforcement; use true for isolated validation clusters"
  type        = bool
  default     = false
}
