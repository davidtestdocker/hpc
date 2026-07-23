output "firewall_name" {
  value = google_compute_firewall.this.name
}

output "firewall_id" {
  value = google_compute_firewall.this.id
}
