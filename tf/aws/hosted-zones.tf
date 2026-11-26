resource "aws_route53_zone" "dyn_oddbit_com" {
  name    = "dyn.oddbit.com"
  comment = "For dynamic dns records"
}

