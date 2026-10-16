output "bucket_name" {
  description = "Name of the S3 bucket."
  value       = aws_s3_bucket.suhas_bucket.bucket
}
output "bucket_arn" {
  description = "ARN of the S3 bucket."
  value       = aws_s3_bucket.suhas_bucket.arn
}
output "bucket_region" {
  description = "AWS region of the S3 bucket."
  value       = aws_s3_bucket.suhas_bucket.region
}
