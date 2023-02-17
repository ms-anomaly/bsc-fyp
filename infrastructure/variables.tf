variable "aws_profile" {
  type        = string
  description = "The name of your AWS profile - can be loaded from environment variables"
}

variable "instance_name" {
  description = "Value of the Name tag for the EC2 instance"
  type        = string
}

variable "ami_ubuntu_22" {
  description = "Value of the image AMI to run on the EC2 instance"
  type        = string
  default = "ami-029562ad87fe1185c"
}

variable "configs" {
  description = "Shared configurations file path"
  type        = string
  default = "~/.aws/tf_user/conf"
}

variable "creds" {
  description = "Shared credentials file path"
  type        = string
  default = "~/.aws/tf_user/creds"
}

variable "vpc_cidr" {
  description = "VPC CIDR"
  type        = string
  default = "178.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "Subnet CIDR"
  type        = string
  default = "178.0.10.0/24"
}