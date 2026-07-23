variable "firewall_name" {
  description = "Firewall rule name"
  type        = string
}

variable "network" {
  description = "VPC network self link"
  type        = string
}

variable "source_ranges" {
  description = "Allowed source ranges"
  type        = list(string)
}
