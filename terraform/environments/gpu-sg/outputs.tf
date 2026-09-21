output "cluster_name" {
  description = "Managed GKE cluster name"
  value       = google_container_cluster.this.name
}

output "cluster_location" {
  description = "Zonal location used by kubectl credential commands"
  value       = google_container_cluster.this.location
}

output "system_pool_name" {
  description = "CPU platform node pool"
  value       = google_container_node_pool.system.name
}

output "gpu_pool_name" {
  description = "L4 time-sharing node pool"
  value       = google_container_node_pool.gpu.name
}
