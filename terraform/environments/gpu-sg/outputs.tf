# 輸出供後續取得 credentials／bootstrap 使用；有輸出不代表 Pod 或工作已健康。
# pool 名稱不能當成實際 node 數量或 GPU readiness 證據。
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
