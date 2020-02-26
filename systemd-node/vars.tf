variable "region" {
  default = "us-east-1"
}
variable "defaultAMI" {
  default = "ami-08bc77a2c7eb2b1da"
}
variable "availabilityZone" {
  default = "us-east-1a"
}
variable "instanceTenancy" {
  default = "default"
}
variable "dnsSupport" {
  default = true
}
variable "dnsHostNames" {
  default = true
}
variable "vpcCIDRblock" {
  default = "10.0.0.0/16"
}
variable "subnetCIDRblock" {
  default = "10.0.1.0/24"
}
variable "destinationCIDRblock" {
  default = "0.0.0.0/0"
}
variable "ingressCIDRblock" {
  default = ["0.0.0.0/0"]
}
variable "egressCIDRblock" {
  default = ["0.0.0.0/0"]
}
variable "mapPublicIP" {
  default = true
}
variable "sshKeyName" {
  default = "jresendiz27-aws_exercises"
}
