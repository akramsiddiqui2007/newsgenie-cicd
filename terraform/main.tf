resource "google_compute_network" "newsgenie_vpc" {
  name                    = var.network_name
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "allow_http_https" {
  name    = "${var.firewall_name_prefix}-allow-http-https"
  network = google_compute_network.newsgenie_vpc.self_link

  direction = "INGRESS"
  priority  = 1000

  source_ranges = ["0.0.0.0/0"]
  target_tags   = [var.instance_tag]

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "${var.firewall_name_prefix}-allow-ssh"
  network = google_compute_network.newsgenie_vpc.self_link

  direction = "INGRESS"
  priority  = 1000

  source_ranges = [var.ssh_source_cidr]
  target_tags   = [var.instance_tag]

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

resource "google_compute_address" "newsgenie_ip" {
  name    = var.static_ip_name
  region  = var.region
  address = var.static_ip_address != "" ? var.static_ip_address : null
}

resource "google_compute_instance" "newsgenie_vm" {
  name         = var.vm_name
  machine_type = var.machine_type
  zone         = var.zone
  tags         = [var.instance_tag]

  metadata = {
    ssh-keys = "${var.ssh_user}:${var.ssh_public_key}"
  }

  boot_disk {
    auto_delete = true
    source      = var.boot_disk_source != "" ? var.boot_disk_source : null

    dynamic "initialize_params" {
      for_each = var.boot_disk_source == "" ? [1] : []
      content {
        image = var.boot_image
      }
    }
  }

  network_interface {
    network = google_compute_network.newsgenie_vpc.self_link

    access_config {
      nat_ip = google_compute_address.newsgenie_ip.address
    }
  }

  lifecycle {
    ignore_changes = [
      metadata
    ]
  }
}
