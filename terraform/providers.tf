provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "tomber-cloud"
      Environment = "dev"
      ManagedBy   = "Terraform"
    }
  }
}