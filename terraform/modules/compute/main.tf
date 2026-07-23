resource "google_compute_instance" "this" {

  name         = var.name
  machine_type = var.machine_type
  zone         = var.zone

allow_stopping_for_update = true

  boot_disk {
    initialize_params {
      image = var.image
    }
  }

  network_interface {
    network = var.network
    subnetwork = var.subnetwork
  }

}
