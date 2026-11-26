resource "aws_cloudwatch_log_group" "update_ddns_record" {
  name = "/aws/lambda/update-ddns-record"
}

resource "aws_iam_role" "update_ddns_record_lambda" {
  name = "update-ddns-record-role-6pq8sx1s"
  path = "/service-role/"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "update_ddns_record_basic_execution" {
  name = "AWSLambdaBasicExecutionRole-cf34bb26-0e04-4d3a-ae09-8f33715ad366"
  path = "/service-role/"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "logs:CreateLogGroup"
        Resource = "arn:aws:logs:us-east-1:979851199135:*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        Resource = [
          "arn:aws:logs:us-east-1:979851199135:log-group:/aws/lambda/update-ddns-record:*",
        ]
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "update_ddns_record_basic_execution" {
  role       = aws_iam_role.update_ddns_record_lambda.name
  policy_arn = aws_iam_policy.update_ddns_record_basic_execution.arn
}

resource "aws_iam_role_policy" "update_ddns_record_route53" {
  name = "allow-dyn-oddbit-com-update"
  role = aws_iam_role.update_ddns_record_lambda.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "VisualEditor0"
      Effect   = "Allow"
      Action   = "route53:ChangeResourceRecordSets"
      Resource = "arn:aws:route53:::hostedzone/${aws_route53_zone.dyn_oddbit_com.zone_id}"
      Condition = {
        "ForAllValues:StringEquals" = {
          "route53:ChangeResourceRecordSetsNormalizedRecordNames" = ["house.dyn.oddbit.com"]
          "route53:ChangeResourceRecordSetsRecordTypes"           = ["A"]
          "route53:ChangeResourceRecordSetsActions"               = ["UPSERT"]
        }
      }
    }]
  })
}

data "vault_kv_secret_v2" "ddns_update_token" {
  mount = "house"
  name  = "gw.house/ddns-update-token"
}

resource "aws_lambda_function" "update_ddns_record" {
  function_name = "update-ddns-record"
  role          = aws_iam_role.update_ddns_record_lambda.arn
  handler       = "bootstrap"
  runtime       = "provided.al2"
  architectures = ["x86_64"]

  filename         = "../../src/update-ddns-record/function.zip"
  source_code_hash = filebase64sha256("../../src/update-ddns-record/function.zip")
  timeout          = 3
  memory_size      = 128

  environment {
    variables = {
      DDNS_HOSTED_ZONE_ID = aws_route53_zone.dyn_oddbit_com.zone_id
      DDNS_UPDATE_TOKEN   = data.vault_kv_secret_v2.ddns_update_token.data["token"]
    }
  }
}

resource "aws_apigatewayv2_api" "update_ddns_record" {
  name          = "update-ddns-record-API"
  protocol_type = "HTTP"
  description   = "Created by AWS Lambda"
}

resource "aws_apigatewayv2_route" "update_ddns_record" {
  api_id    = aws_apigatewayv2_api.update_ddns_record.id
  route_key = "ANY /update-ddns-record"
  target    = "integrations/wijxzce"
}

resource "aws_apigatewayv2_stage" "update_ddns_record_named" {
  api_id      = aws_apigatewayv2_api.update_ddns_record.id
  name        = "default"
  auto_deploy = true
  description = "Created by AWS Lambda"
}

resource "aws_lambda_permission" "update_ddns_record_apigw" {
  statement_id  = "lambda-f6633b4c-2bbc-4d22-bec7-f6ab57ef0d8c"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_ddns_record.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:us-east-1:979851199135:${aws_apigatewayv2_api.update_ddns_record.id}/*/*/update-ddns-record"
}
