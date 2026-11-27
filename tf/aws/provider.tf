terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.74"
    }
    vault = {
      source  = "hashicorp/vault"
      version = "~> 5.14"
    }
  }
}

provider "vault" {
  address = "https://bao.keg.house"
}

provider "aws" {
  region = "us-east-1"

  # This applies the "managed-by:" tag to all resources created by this
  # repository. This is useful in e.g. resource explorer queries to identify
  # unmanaged resources.
  #
  # aws resource-explorer-2 search --query-string='-tag:managed-by=...'
  default_tags {
    tags = {
      managed-by = "house.oddbit.com"
    }
  }
}
