variable "aws_region" {
  description = "AWS region for the Session 19 mini project."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix for the project's bucket, instance role, and instance."
  type        = string
  default     = "session19-suhas"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,29}$", var.project_name))
    error_message = "Use 3-30 lowercase letters, digits, or hyphens, starting with a letter."
  }
}

variable "instance_type" {
  description = "x86_64 EC2 instance type compatible with the selected Amazon Linux image."
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "Optional regional x86_64 Amazon Linux 2023 AMI; null uses AWS's public SSM parameter."
  type        = string
  default     = null

  validation {
    condition     = var.ami_id == null ? true : can(regex("^ami-[0-9a-f]{8}([0-9a-f]{9})?$", var.ami_id))
    error_message = "Use a valid AMI ID or leave ami_id unset."
  }
}

variable "http_allowed_cidr" {
  description = "IPv4 clients allowed to access the demo HTTP page."
  type        = string
  default     = "0.0.0.0/0"

  validation {
    condition     = can(cidrnetmask(var.http_allowed_cidr))
    error_message = "Use an IPv4 CIDR range."
  }
}
