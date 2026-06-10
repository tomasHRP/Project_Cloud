# Setup

Este documento descreve os requisitos necessários para preparar o ambiente local e a conta AWS antes de executar ou fazer deploy do projeto.

## Pré-requisitos Locais

A máquina local deve ter instaladas as seguintes ferramentas:

- Git
- Docker
- Docker Compose
- Terraform
- Ansible
- AWS CLI
- Python, caso os serviços sejam desenvolvidos em Python
- Acesso a uma conta AWS

## Pré-requisitos AWS

A conta AWS deve permitir criar e gerir os seguintes recursos:

- VPC
- Subnets
- Route Tables
- Internet Gateway
- Security Groups
- EC2
- RDS
- SQS
- IAM Roles e Policies

## Configuração da AWS CLI

Configurar a AWS CLI:

```bash
aws configure
```

Valores necessários:

```text
AWS Access Key ID
AWS Secret Access Key
Default region: us-east-1
Default output format: json
```

As credenciais da AWS não devem ser guardadas diretamente no código.

Para GitHub Actions, devem ser usados GitHub Secrets ou, idealmente, OIDC.

## Variáveis de Ambiente

Para execução local, pode ser usado um ficheiro `.env`.

Exemplo:

```env
AWS_REGION=us-east-1
SQS_QUEUE_URL=<url-da-fila-sqs>

DB_HOST=<endpoint-da-base-de-dados>
DB_PORT=5432
DB_NAME=<nome-da-base-de-dados>
DB_USER=<utilizador>
DB_PASSWORD=<password>

ORDER_SERVICE_URL=http://order-service:8000
```

O ficheiro `.env` não deve ser enviado para o GitHub.

## Estrutura Esperada do Projeto

```text
project-root/
├── README.md
├── docker-compose.yml
├── .github/
│   └── workflows/
│       └── deploy.yml
├── infra/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── terraform.tfvars
│   └── modules/
├── ansible/
│   ├── inventory.ini
│   └── playbook.yml
├── services/
│   ├── api-gateway/
│   │   └── Dockerfile
│   ├── order-service/
│   │   └── Dockerfile
│   └── worker-service/
│       └── Dockerfile
└── docs/
    ├── architecture.md
    ├── setup.md
    ├── deployment.md
    ├── security.md
    └── limitations.md
```

## Executar Localmente

Na raiz do projeto:

```bash
docker compose up --build
```

Verificar containers:

```bash
docker ps
```

Testar o endpoint de saúde:

```bash
curl http://localhost/health
```

Caso os serviços estejam expostos em portas diferentes:

```bash
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## Verificar Logs Localmente

```bash
docker logs api-gateway
docker logs order-service
docker logs worker-service
```

## Ficheiros Sensíveis

Os seguintes ficheiros não devem ser enviados para o repositório:

```text
.env
*.pem
terraform.tfstate
terraform.tfstate.backup
.terraform/
```

Estes ficheiros devem estar incluídos no `.gitignore`.
