resource "docker_image" "taskflow" {
  name         = var.image_name
  keep_locally = true
}

resource "docker_container" "taskflow" {
  name    = var.application_name
  image   = docker_image.taskflow.image_id
  restart = "unless-stopped"

  ports {
    internal = 8501
    external = var.host_port
  }

  volumes {
    volume_name    = "${var.application_name}-data"
    container_path = "/data"
  }
}
