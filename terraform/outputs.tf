output "container_name" {
  description = "Name of the provisioned TaskFlow container."
  value       = docker_container.taskflow.name
}

output "application_url" {
  description = "URL for the TaskFlow dashboard."
  value       = "http://localhost:${var.host_port}"
}
