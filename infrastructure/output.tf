output "server_private_ip" {
  description = "ID of the EC2 instance"
  value = aws_instance.app_server.private_ip
}

output "server_public_ipv4" {
  description = "Public IP address of the EC2 instance"
  value = aws_instance.app_server.public_ip
}

output "server_id" {
  value = aws_instance.app_server.id
}