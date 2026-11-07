terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# ---------- DynamoDB ----------
resource "aws_dynamodb_table" "swipes" {
  name         = "swipes"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "swiper_id"
  range_key    = "swipee_id"

  attribute {
    name = "swiper_id"
    type = "S"
  }
  attribute {
    name = "swipee_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "matches" {
  name         = "matches"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "match_user_id"

  attribute {
    name = "user_id"
    type = "S"
  }
  attribute {
    name = "match_user_id"
    type = "S"
  }
}

# ---------- Security group ----------
resource "aws_security_group" "api" {
  name        = "swipe-match-sg"
  description = "HTTP for API, SSH from my IP"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------- EC2 ----------
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

resource "aws_instance" "api" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.api.id]

  # AWS Academy: pre-created profile wrapping LabRole (has DynamoDB access)
  iam_instance_profile = "LabInstanceProfile"

  # Containers are one network hop away; hop limit 2 lets boto3 get role credentials
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    repo_url      = var.repo_url
    region        = var.region
    swipes_table  = aws_dynamodb_table.swipes.name
    matches_table = aws_dynamodb_table.matches.name
  })
  user_data_replace_on_change = true

  tags = {
    Name = "swipe-match-service"
  }
}
