from lib import secrets

# Evaluated once when group_data is loaded; accessible via host.data.ddns_update_token
ddns_update_token = secrets.read_secret("house/gw.house/ddns-update-token", key="token")

# API Gateway invoke URL for the update-ddns-record Lambda. Not read from
# Terraform state (this repo doesn't read `tofu output`); copy this from the
# `aws_apigatewayv2_api` resource / `tofu output` in tf/aws if it ever changes.
ddns_update_url = (
    "https://d5rjkt0gv8.execute-api.us-east-1.amazonaws.com/update-ddns-record"
)
