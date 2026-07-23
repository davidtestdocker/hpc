resource "google_compute_firewall" "this" {
  name    = var.firewall_name
  network = var.network

  allow {
    protocol = "tcp"

    ports = [
      "22",
      "8000"
    ]
  }

  source_ranges = var.source_ranges
}
