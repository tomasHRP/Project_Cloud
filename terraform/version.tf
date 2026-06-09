terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "cloudfinalprojtomber"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tomber-cloud"
    encrypt        = true
  }
}