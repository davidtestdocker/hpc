module "network" {
  source = "../../modules/network"

  network_name = "hpc-${var.environment}-vpc"
  subnet_name  = "hpc-${var.environment}-subnet"
  subnet_cidr  = var.subnet_cidr
  region       = var.region
}

module "firewall" {
  source = "../../modules/firewall"

  firewall_name = "hpc-${var.environment}-firewall"
  network       = module.network.network_self_link

  source_ranges = [
    "0.0.0.0/0"
  ]
}

module "api" {
  source = "../../modules/compute"

  name         = "hpc-api-${var.environment}"
  machine_type = "e2-medium"
  zone         = var.zone
  image        = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"

  network    = module.network.network_id
  subnetwork = module.network.subnet_id
}
