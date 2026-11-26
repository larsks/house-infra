output "name" {
  value = aws_iam_user.this.name
}

output "arn" {
  value = aws_iam_user.this.arn
}

output "access_keys" {
  value = {
    for label, key in aws_iam_access_key.this : label => {
      id     = key.id
      secret = key.secret
    }
  }
  sensitive = true
}

