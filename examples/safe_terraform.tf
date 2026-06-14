resource "aws_s3_bucket" "dev_logs" {
  bucket = "arkstride-dev-logs"
}

resource "aws_s3_bucket_public_access_block" "dev_logs" {
  bucket = aws_s3_bucket.dev_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}