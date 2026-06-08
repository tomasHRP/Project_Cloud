# Architecture

## Overview

This project is a simple cloud-based microservices application deployed on AWS.

The application will use Docker containers running on an EC2 instance. The infrastructure will be created with Terraform, and the deployment will be automated with GitHub Actions and Ansible.

The system has three main services:

* `api-gateway`
* `order-service`
* `worker-service`

The `api-gateway` receives HTTP requests from users and forwards them to the internal services. The `order-service` manages orders and stores data in a database. The `worker-service` processes asynchronous messages from an SQS queue.

## Architecture Diagram

```text
User
  |
  v
Internet
  |
  v
EC2 Instance
  |
  |---- api-gateway
  |
  |---- order-service
  |        |
  |        v
  |      RDS Database
  |
  |---- worker-service
           ^
           |
        SQS Queue
```

## AWS Infrastructure

The project will be deployed in the `us-east-1` AWS region.

The infrastructure will include:

* VPC
* Public subnets
* Private subnets
* Internet Gateway
* Security groups
* EC2 instance
* RDS database
* SQS queue
* Dead Letter Queue
* S3 bucket for Terraform remote state
* DynamoDB table for Terraform state locking

## Service Boundaries

### api-gateway

The `api-gateway` is the public entry point of the application. It receives HTTP requests from users and routes them to the correct internal service.

### order-service

The `order-service` manages order-related operations. It stores order data in the RDS database and sends messages to SQS when an order is created.

### worker-service

The `worker-service` consumes messages from SQS and processes background tasks related to orders.

## Data Flow

```text
1. The user sends a request to the api-gateway.
2. The api-gateway forwards the request to the order-service.
3. The order-service stores the order in the RDS database.
4. The order-service sends a message to SQS.
5. The worker-service consumes the message from SQS.
6. The worker-service processes the order.
7. The database is updated with the final order status.
```

## Deployment Flow

```text
Developer
  |
  v
GitHub
  |
  v
GitHub Actions
  |
  |---- Terraform
  |---- Docker build
  |---- Docker push
  |---- Ansible deploy
  |
  v
AWS EC2
```

## Naming Convention

All AWS resources will use the following naming pattern:

```text
tomas-cloud-dev-resource-name
```

Examples:

```text
tomas-cloud-dev-vpc
tomas-cloud-dev-ec2
tomas-cloud-dev-rds
tomas-cloud-dev-sqs
tomas-cloud-dev-dlq
tomas-cloud-dev-sg-web
tomas-cloud-dev-sg-db
```

## Branching Strategy

The project will use the following branches:

```text
main
dev
feature/*
```

Development will be done in `feature/*` branches. Pull requests will be used before merging into `main`.

The `main` branch will be protected and will be used for production deployment.

## Technology Choices

| Area                   | Technology            |
| ---------------------- | --------------------- |
| Cloud Provider         | AWS                   |
| Region                 | us-east-1             |
| Infrastructure as Code | Terraform             |
| Deployment             | Ansible               |
| CI/CD                  | GitHub Actions        |
| Compute                | EC2                   |
| Containers             | Docker                |
| Database               | Amazon RDS PostgreSQL |
| Queue                  | Amazon SQS            |
| Version Control        | GitHub                |
