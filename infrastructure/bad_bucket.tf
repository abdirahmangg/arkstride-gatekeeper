resource "aws_s3_bucket" "prod_data" {
  bucket = "arkstride-prod-live-customer-data"
}

resource "aws_s3_bucket_public_access_block" "prod_data" {
  bucket = aws_s3_bucket.prod_data.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
