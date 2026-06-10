output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value = [
    aws_subnet.public_1a.id,
    aws_subnet.public_1b.id
  ]
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value = [
    aws_subnet.private_1a.id,
    aws_subnet.private_1b.id
  ]
}

output "web_security_group_id" {
  description = "Security group ID for the web tier"
  value       = aws_security_group.web.id
}

output "db_security_group_id" {
  description = "Security group ID for the database tier"
  value       = aws_security_group.db.id
}
/////////////////4////////////////////////
output "ec2_public_ip" {
  description = "Public IP address of the EC2 application server"
  value       = aws_instance.app.public_ip
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_database_name" {
  description = "RDS database name"
  value       = aws_db_instance.postgres.db_name
}

output "orders_queue_url" {
  description = "URL of the orders SQS queue"
  value       = aws_sqs_queue.orders.url
}

output "orders_queue_arn" {
  description = "ARN of the orders SQS queue"
  value       = aws_sqs_queue.orders.arn
}

output "orders_dlq_url" {
  description = "URL of the orders dead-letter queue"
  value       = aws_sqs_queue.orders_dlq.url
}