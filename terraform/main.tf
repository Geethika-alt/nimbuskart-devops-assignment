locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

module "network" {
  source = "./modules/network"

  vpc_cidr = "10.20.0.0/16"

  public_subnet_cidrs = [
    "10.20.1.0/24",
    "10.20.2.0/24"
  ]

  availability_zones = [
    "us-east-1a",
    "us-east-1b"
  ]

  tags = local.common_tags
}

resource "aws_security_group" "web_sg" {
  name        = "web-security-group"
  description = "Allow web and SSH traffic"
  vpc_id      = module.network.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_ingress_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "web-security-group"
  })
}

resource "aws_instance" "web" {
  count = 2

  ami                    = "ami-12345678"
  instance_type          = "t3.micro"
  subnet_id              = module.network.public_subnet_ids[count.index]
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  tags = merge(local.common_tags, {
    Name = "web-instance-${count.index + 1}"
    Tier = "web"
  })
}

resource "aws_s3_bucket" "logs" {
  bucket = "nimbuskart-staging-logs"

  tags = merge(local.common_tags, {
    Name = "logs-bucket"
  })
}

resource "aws_s3_bucket_versioning" "logs" {
  bucket = aws_s3_bucket.logs.id

  versioning_configuration {
    status = "Enabled"
  }
}


resource "aws_ebs_volume" "orphan_volume" {
  availability_zone = "us-east-1a"
  size              = 10

  tags = merge(local.common_tags, {
    Name = "orphan-ebs-volume"
  })
}
