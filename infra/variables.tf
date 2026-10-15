variable "region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "prod"
}

variable "vpc_cidr" {
  type    = string
  default = "10.20.0.0/16"
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.medium"
}

variable "api_max_concurrency" {
  description = "Reserved Lambda concurrency; also the most Postgres connections the API can open"
  type        = number
  default     = 50
}

variable "alarm_email" {
  description = "Where CloudWatch alarms are sent"
  type        = string
}

variable "api_package_path" {
  description = "Path to the zipped API build produced by the deploy pipeline"
  type        = string
  default     = "../api/dist/api.zip"
}

variable "jwt_issuer" {
  description = "OIDC issuer of the company SSO, e.g. https://sso.example.com"
  type        = string
}

variable "jwt_audience" {
  type    = list(string)
  default = ["shelf"]
}

variable "bastion_key_name" {
  description = "EC2 key pair for the bastion host"
  type        = string
}
