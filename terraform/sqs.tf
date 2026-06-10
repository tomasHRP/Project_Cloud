resource "aws_sqs_queue" "orders_dlq" {
  name = "${local.name_prefix}-orders-dlq"

  message_retention_seconds = 1209600

  tags = {
    Name = "${local.name_prefix}-orders-dlq"
  }
}

resource "aws_sqs_queue" "orders" {
  name = "${local.name_prefix}-orders-queue"

  visibility_timeout_seconds = 30
  message_retention_seconds  = 345600

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.orders_dlq.arn
    maxReceiveCount     = 3
  })

  tags = {
    Name = "${local.name_prefix}-orders-queue"
  }
}