resource "aws_iam_user" "this" {
  name = var.name
  tags = var.tags
  path = var.path
}

resource "aws_iam_access_key" "this" {
  for_each = var.access_keys
  user     = aws_iam_user.this.name
}

resource "aws_iam_user_policy_attachment" "this" {
  for_each   = var.policy_arns
  user       = aws_iam_user.this.name
  policy_arn = each.value
}
