provider "aws" {
    profile = "default"
    region = "us-east-1"
}

resource "aws_instance" "blog" {
  ami = "ami-097ba1da3bf55a025"
  instance_type = "t2.small"
}