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


module "gke" {

  source       = "../../modules/gke"
  project_id   = var.project_id
  region       = var.region
  zone         = var.zone
  cluster_name = "hpc-dev"
  network      = module.network.network_name
  subnetwork   = module.network.subnet_name
  node_count   = 1
  machine_type = "e2-standard-2"
}
