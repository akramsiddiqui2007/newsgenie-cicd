output "vm_name" {
  value = google_compute_instance.newsgenie_vm.name
}

output "vm_zone" {
  value = google_compute_instance.newsgenie_vm.zone
}

output "network_name" {
  value = google_compute_network.newsgenie_vpc.name
}

output "http_https_firewall_name" {
  value = google_compute_firewall.allow_http_https.name
}

output "ssh_firewall_name" {
  value = google_compute_firewall.allow_ssh.name
}

output "static_ip" {
  value = google_compute_address.newsgenie_ip.address
}
