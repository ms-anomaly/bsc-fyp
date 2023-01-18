provider "aws" {
    region  = "ap-southeast-1"
    shared_config_files      = [var.configs]
    shared_credentials_files = [var.creds]
    profile = var.aws_profile
}