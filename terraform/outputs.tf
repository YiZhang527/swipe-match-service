output "public_ip" {
  value = aws_instance.api.public_ip
}

output "api_url" {
  value = "http://${aws_instance.api.public_ip}"
}
