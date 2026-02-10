variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Prefix for resources"
  default     = "mlops-demo"
}

variable "container_port" {
  type        = number
  default     = 8080
}
