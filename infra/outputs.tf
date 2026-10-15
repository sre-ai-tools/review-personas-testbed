output "api_url" {
  value = aws_apigatewayv2_api.main.api_endpoint
}

output "web_url" {
  value = "https://${aws_cloudfront_distribution.web.domain_name}"
}

output "db_endpoint" {
  value = aws_db_instance.main.address
}
