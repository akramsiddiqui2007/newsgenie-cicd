variable "project_id" {
  type        = string
  description = "GCP project ID"
  default     = "project-8be6a108-f8c8-4ef9-879"
}

variable "region" {
  type        = string
  description = "GCP region"
  default     = "us-central1"
}

variable "zone" {
  type        = string
  description = "GCP zone"
  default     = "us-central1-a"
}

variable "network_name" {
  type        = string
  description = "VPC network name"
  default     = "newsgenie-vpc"
}

variable "vm_name" {
  type        = string
  description = "VM instance name"
  default     = "newsgenie-vm"
}

variable "machine_type" {
  type        = string
  description = "GCE machine type"
  default     = "e2-standard-2"
}

variable "instance_tag" {
  type        = string
  description = "Network tag for firewall targeting"
  default     = "newsgenie"
}

variable "firewall_name_prefix" {
  type        = string
  description = "Prefix for firewall rule names"
  default     = "newsgenie"
}

variable "static_ip_name" {
  type        = string
  description = "Static external IP resource name"
  default     = "newsgenie-ip"
}

variable "static_ip_address" {
  type        = string
  description = "Static external IP address; set empty string to let GCP allocate one"
  default     = "34.172.127.95"
}

variable "ssh_source_cidr" {
  type        = string
  description = "CIDR allowed to SSH to the VM"
  default     = "121.6.250.135/32"
}

variable "ssh_user" {
  type        = string
  description = "SSH username for instance metadata key"
  default     = "akram"
}

variable "ssh_public_key" {
  type        = string
  description = "Public SSH key to keep on the VM metadata"
  default     = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHicDLNimxcqkc8msUOMM8GlMUHgqCrUlgfF6Kfgr8QJ newsgenie-oci"
}

variable "boot_disk_source" {
  type        = string
  description = "Existing boot disk self-link/path for imported VM; empty string for a fresh VM from image"
  default     = "projects/project-8be6a108-f8c8-4ef9-879/zones/us-central1-a/disks/newsgenie-vm"
}

variable "boot_image" {
  type        = string
  description = "Boot image to use when creating a fresh VM"
  default     = "projects/ubuntu-os-cloud/global/images/family/ubuntu-2204-lts"
}
