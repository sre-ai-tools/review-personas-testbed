terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }

  backend "s3" {
    bucket         = "shelf-terraform-state"
    key            = "shelf/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "shelf-terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "shelf"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
