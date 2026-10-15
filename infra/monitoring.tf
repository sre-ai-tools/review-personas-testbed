resource "aws_sns_topic" "alarms" {
  name              = "shelf-alarms-${var.environment}"
  kms_master_key_id = "alias/aws/sns"
}

resource "aws_sns_topic_subscription" "alarms_email" {
  topic_arn = aws_sns_topic.alarms.arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

locals {
  alarms = {
    lambda-errors = {
      namespace = "AWS/Lambda", metric = "Errors", stat = "Sum", threshold = 5
      dimensions = { FunctionName = aws_lambda_function.api.function_name }
    }
    lambda-throttles = {
      namespace = "AWS/Lambda", metric = "Throttles", stat = "Sum", threshold = 1
      dimensions = { FunctionName = aws_lambda_function.api.function_name }
    }
    api-5xx = {
      namespace = "AWS/ApiGateway", metric = "5xx", stat = "Sum", threshold = 5
      dimensions = { ApiId = aws_apigatewayv2_api.main.id, Stage = "$default" }
    }
    db-cpu = {
      namespace = "AWS/RDS", metric = "CPUUtilization", stat = "Average", threshold = 80
      dimensions = { DBInstanceIdentifier = aws_db_instance.main.identifier }
    }
    db-connections = {
      namespace = "AWS/RDS", metric = "DatabaseConnections", stat = "Maximum", threshold = var.api_max_concurrency * 0.8
      dimensions = { DBInstanceIdentifier = aws_db_instance.main.identifier }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "this" {
  for_each = local.alarms

  alarm_name          = "shelf-${var.environment}-${each.key}"
  namespace           = each.value.namespace
  metric_name         = each.value.metric
  statistic           = each.value.stat
  dimensions          = each.value.dimensions
  period              = 300
  evaluation_periods  = 1
  threshold           = each.value.threshold
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [aws_sns_topic.alarms.arn]
  ok_actions          = [aws_sns_topic.alarms.arn]
}
