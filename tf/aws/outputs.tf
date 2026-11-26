output "iam_users" {
  value = {
    for name, user in module.iam_user : name => {
      name = user.name
      arn  = user.arn
    }
  }
}

output "iam_user_access_keys" {
  value     = { for name, user in module.iam_user : name => user.access_keys }
  sensitive = true
}
