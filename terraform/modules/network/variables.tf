variable "network_name" {
  description = "VPC network name"
  type        = string
}

variable "subnet_name" {
  description = "Subnet name"
  type        = string
}

variable "subnet_cidr" {
  description = "Subnet IPv4 CIDR range"
  type        = string
}

variable "region" {
  description = "Subnet region"
  type        = string
}
