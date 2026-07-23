output "name" {
  description = "Compute instance name"
  value       = google_compute_instance.this.name
}

output "zone" {
  description = "Compute instance zone"
  value       = google_compute_instance.this.zone
}

output "internal_ip" {
  description = "Compute instance internal IP"
  value       = google_compute_instance.this.network_interface[0].network_ip
}

output "machine_type" {
  description = "Compute instance machine type"
  value       = google_compute_instance.this.machine_type
}
