output "network_id" {
  description = "VPC network ID"
  value       = google_compute_network.this.id
}

output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.this.name
}

output "network_self_link" {
  description = "VPC network self link"
  value       = google_compute_network.this.self_link
}

output "subnet_id" {
  description = "Subnet ID"
  value       = google_compute_subnetwork.this.id
}

output "subnet_name" {
  description = "Subnet name"
  value       = google_compute_subnetwork.this.name
}

output "subnet_self_link" {
  description = "Subnet self link"
  value       = google_compute_subnetwork.this.self_link
}
