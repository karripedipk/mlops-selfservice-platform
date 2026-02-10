output "alb_dns_name" {
  value = aws_lb.this.dns_name
}

output "artifact_bucket" {
  value = aws_s3_bucket.artifacts.bucket
}

output "model_pointer_ssm_param" {
  value = aws_ssm_parameter.model_pointer.name
}

output "ecr_serving_repo" {
  value = aws_ecr_repository.serving.repository_url
}
