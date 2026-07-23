output "vm_name" {
  description = "VM Name"
  value       = module.api.name
}

output "vm_zone" {
  description = "VM Zone"
  value       = module.api.zone
}

output "vm_internal_ip" {
  description = "VM internal IP address"
  value       = module.api.internal_ip
}

output "vm_machine_type" {
  description = "VM machine type"
  value       = module.api.machine_type
}
