output "vpc_id" {
  value = aws_vpc.main.id
}

output "vpc_cidr" {
  value = aws_vpc.main.cidr_block
}

output "subnet_id" {
  value = aws_subnet.public.id
}

output "security_group_id" {
  value = aws_security_group.web.id
}

output "instance_id" {
  description = "EC2 web server ID."
  value       = aws_instance.web.id
}

output "web_url" {
  description = "HTTP endpoint after the instance bootstrap completes."
  value       = "http://${aws_instance.web.public_ip}"
}

output "artifact_bucket" {
  description = "Private versioned bucket holding site/index.html."
  value       = aws_s3_bucket.artifacts.id
}
