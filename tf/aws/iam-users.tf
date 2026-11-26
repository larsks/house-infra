# Single source of truth for IAM users managed via the iam-user module.
# Add a new entry here to provision another user; outputs.tf picks it up
# automatically.
locals {
  iam_users = {}
}

module "iam_user" {
  source   = "./modules/iam-user"
  for_each = local.iam_users

  name        = each.key
  tags        = try(each.value.tags, {})
  access_keys = try(each.value.access_keys, {})
  policy_arns = try(each.value.policy_arns, {})
  path        = try(each.value.path, "/")
}
