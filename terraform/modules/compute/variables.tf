variable "name" {
  description = "Compute instance name"
  type        = string
}

variable "machine_type" {
  description = "Compute instance machine type"
  type        = string
}

variable "zone" {
  description = "Compute instance zone"
  type        = string
}

variable "image" {
  description = "Boot disk image"
  type        = string
}

variable "network" {
  description = "VPC network name or self link"
  type        = string
}

variable "subnetwork" {
  description = "Subnet ID or self link"
  type        = string
}
