variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region for deployment"
  type        = string
  default     = "asia-south1"
}

variable "aws_region" {
  description = "AWS Region for Security Hub"
  type        = string
  default     = "us-east-1"
}

variable "azure_subscription_id" {
  description = "Azure Subscription ID for Security Center"
  type        = string
  default     = ""
}
