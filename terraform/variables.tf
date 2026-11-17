variable "application_name" {
  description = "Name used for the TaskFlow container."
  type        = string
  default     = "taskflow"
}

variable "image_name" {
  description = "Name and tag of the TaskFlow image already built locally."
  type        = string
  default     = "taskflow:latest"
}

variable "host_port" {
  description = "Host port that exposes TaskFlow."
  type        = number
  default     = 8501
  validation {
    condition     = var.host_port > 0 && var.host_port < 65536
    error_message = "host_port must be between 1 and 65535."
  }
}
