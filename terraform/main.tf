terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_s3_bucket" "example" {
  bucket = "my-tf-test-bucket-1234-ivan-mlops-club"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}
