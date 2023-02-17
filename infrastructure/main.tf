terraform {
    required_providers {
        aws = {
        source  = "hashicorp/aws"
        version = "~> 4.16"
        }
    }

    required_version = ">= 1.2.0"
}

resource "aws_instance" "app_server" {
    ami           = var.ami_ubuntu_22
    instance_type = "t2.large"
    key_name = "tf-key-pair"
    subnet_id       = aws_subnet.public_subnet.id
    security_groups = [aws_security_group.fyp_sg.id]

    tags = {
        Name = var.instance_name
    }

    user_data = file("linux_init.sh")

    ebs_block_device {
        device_name = "/dev/sda1"
        volume_size = 20
        volume_type = "gp2"
    }
}

resource "aws_key_pair" "tf-key-pair" {
    key_name = "tf-key-pair"
    public_key = tls_private_key.rsa.public_key_openssh
}

resource "tls_private_key" "rsa" {
    algorithm = "RSA"
    rsa_bits  = 4096
}

resource "local_file" "tf-key" {
    content  = tls_private_key.rsa.private_key_pem
    filename = "tf-key-pair"
}
