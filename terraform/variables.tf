variable "region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "key_name" {
  description = "Existing EC2 key pair name (e.g. vockey in AWS Academy)"
  type        = string
  default     = "vockey"
}

variable "my_ip_cidr" {
  description = "Your IP for SSH, e.g. 1.2.3.4/32"
  type        = string
}

variable "repo_url" {
  description = "Public GitHub repo URL to clone"
  type        = string
}
