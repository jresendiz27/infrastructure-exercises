provider "aws" {
  profile = "default"
  region  = var.region
}

resource "aws_vpc" "poorman_system_monitoring_vpc" {
  cidr_block           = var.vpcCIDRblock
  instance_tenancy     = var.instanceTenancy
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "poorman_system_monitoring_vpc"
  }
}

resource "aws_subnet" "poorman_system_monitoring_subnet" {
  vpc_id                  = aws_vpc.poorman_system_monitoring_vpc.id
  cidr_block              = var.subnetCIDRblock
  availability_zone       = var.availabilityZone
  map_public_ip_on_launch = var.mapPublicIP
  tags = {
    Name = "poorman_system_monitoring_subnet"
  }
}

resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Allow ssh inbound traffic"
  vpc_id      = aws_vpc.poorman_system_monitoring_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
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
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_network_acl" "poorman_system_monitoring_network_acl" {
  vpc_id = aws_vpc.poorman_system_monitoring_vpc.id
  subnet_ids = [
    aws_subnet.poorman_system_monitoring_subnet.id
  ]

  ingress {
    action     = "allow"
    from_port  = 22
    protocol   = "tcp"
    cidr_block = var.destinationCIDRblock
    rule_no    = 100
    to_port    = 22
  }
  ingress {
    action     = "allow"
    from_port  = 80
    protocol   = "tcp"
    cidr_block = var.destinationCIDRblock
    rule_no    = 200
    to_port    = 80
  }
  ingress {
    action     = "allow"
    from_port  = 1024
    to_port    = 65535
    protocol   = "tcp"
    cidr_block = var.destinationCIDRblock
    rule_no    = 300
  }
  egress {
    action     = "allow"
    from_port  = 22
    protocol   = "tcp"
    cidr_block = var.destinationCIDRblock
    rule_no    = 100
    to_port    = 22
  }
  egress {
    protocol   = "tcp"
    rule_no    = 200
    action     = "allow"
    cidr_block = var.destinationCIDRblock
    from_port  = 80
    to_port    = 80
  }
  egress {
    protocol   = "tcp"
    rule_no    = 300
    action     = "allow"
    cidr_block = var.destinationCIDRblock
    from_port  = 1024
    to_port    = 65535
  }
  egress {
    action     = "allow"
    from_port  = 0
    protocol   = "tcp"
    cidr_block = var.destinationCIDRblock
    rule_no    = 99
    to_port    = 65535
  }
  tags = {
    Name = "poorman_system_monitoring_ACL"
  }
}

resource "aws_internet_gateway" "systemd_node_internet_gateway" {
  vpc_id = aws_vpc.poorman_system_monitoring_vpc.id
  tags = {
    Name = "systemd_node_internet_gateway"
  }
}

resource "aws_route_table" "systemd_node_route_table" {
  vpc_id = aws_vpc.poorman_system_monitoring_vpc.id
  tags = {
    Name = "systemd_node_route_table"
  }
}

resource "aws_route" "systemd_node_route" {
  route_table_id         = aws_route_table.systemd_node_route_table.id
  destination_cidr_block = var.destinationCIDRblock
  gateway_id             = aws_internet_gateway.systemd_node_internet_gateway.id
}

resource "aws_route_table_association" "systemd_node_table_association" {
  route_table_id = aws_route_table.systemd_node_route_table.id
  subnet_id      = aws_subnet.poorman_system_monitoring_subnet.id
}

resource "aws_instance" "poorman_system_monitoring" {
  ami                         = var.defaultAMI
  instance_type               = "t3a.nano"
  key_name                    = var.sshKeyName
  subnet_id                   = aws_subnet.poorman_system_monitoring_subnet.id
  associate_public_ip_address = true
  tags = {
    Name = "poorman_system_monitoring"
  }
  availability_zone = var.availabilityZone
  vpc_security_group_ids = [
    aws_security_group.allow_ssh.id
  ]
  depends_on = [aws_security_group.allow_ssh]
}

resource "aws_instance" "poorman_system_monitoring_2" {
  ami                         = var.defaultAMI
  instance_type               = "t3a.nano"
  key_name                    = var.sshKeyName
  subnet_id                   = aws_subnet.poorman_system_monitoring_subnet.id
  associate_public_ip_address = true
  tags = {
    Name = "poorman_system_monitoring"
  }
  availability_zone = var.availabilityZone
  vpc_security_group_ids = [
    aws_security_group.allow_ssh.id
  ]
  depends_on = [aws_security_group.allow_ssh]
}

resource "aws_instance" "poorman_system_monitoring_3" {
  ami                         = var.defaultAMI
  instance_type               = "t3a.nano"
  key_name                    = var.sshKeyName
  subnet_id                   = aws_subnet.poorman_system_monitoring_subnet.id
  associate_public_ip_address = true
  tags = {
    Name = "poorman_system_monitoring"
  }
  availability_zone = var.availabilityZone
  vpc_security_group_ids = [
    aws_security_group.allow_ssh.id
  ]
  depends_on = [aws_security_group.allow_ssh]
}