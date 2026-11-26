variable "name" {
  description = "Name of the IAM user"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the IAM user"
  type        = map(string)
  default     = {}
}

variable "access_keys" {
  description = "Map of access key labels to descriptions"
  type        = map(string)
  default     = {}
}

variable "policy_arns" {
  description = "Map of managed policy ARNs to attach to the user (key = stable name, value = ARN)"
  type        = map(string)
  default     = {}
}

variable "path" {
  description = "Used to organize users in a hierarchical structure"
  type        = string
  default     = "/"

  validation {
    condition     = can(regex("^/([a-zA-Z0-9/]+/)?$", var.path))
    error_message = "Path must begin and end with / and contain only alphanumeric characters and / characters."
  }
}
