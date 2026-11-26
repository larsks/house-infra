terraform {
  backend "s3" {
    bucket = "house-tf-state"
    key    = "aws"
    region = "garage"
    endpoints = {
      s3 = "https://s3.garage.keg.house"
    }

    # Required for most non-AWS S3-compatible providers
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    skip_s3_checksum            = true
    use_path_style              = true
  }
}
