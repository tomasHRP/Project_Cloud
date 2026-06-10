# `README.md`

````markdown
# Project Cloud

Projeto de Cloud desenvolvido no âmbito da unidade curricular de Cloud Computing.

O objetivo do projeto é demonstrar uma arquitetura cloud funcional usando AWS, Terraform, Docker, Ansible, GitHub Actions, Amazon RDS, Amazon SQS e Amazon ECR.

A aplicação segue uma arquitetura simples de microserviços, composta por:

- `api-gateway`
- `order-service`
- `worker-service`

O sistema permite criar pedidos/orders através de uma API HTTP. Quando uma order é criada, o `order-service` guarda os dados na base de dados PostgreSQL e envia uma mensagem para uma fila SQS. O `worker-service` consome essa mensagem e atualiza o estado da order para `PROCESSED`.

## Tecnologias utilizadas

| Área | Tecnologia |
|---|---|
| Cloud Provider | AWS |
| IaC | Terraform |
| Compute | EC2 |
| Base de dados | Amazon RDS PostgreSQL |
| Mensageria | Amazon SQS |
| Container Registry | Amazon ECR |
| Containers | Docker |
| Deploy | Ansible |
| CI/CD | GitHub Actions |
| Linguagem da aplicação | Python Flask |
| Versionamento | GitHub |

## Serviços da aplicação

### api-gateway

É o ponto de entrada público da aplicação. Recebe pedidos HTTP e encaminha-os para o `order-service`.

Endpoints principais:

```text
GET /health
POST /orders
GET /orders
````

### order-service

Responsável por criar e listar orders. Este serviço comunica com a base de dados PostgreSQL e envia mensagens para a fila SQS quando uma nova order é criada.

### worker-service

Responsável por consumir mensagens da fila SQS. Quando recebe uma mensagem, processa a order e atualiza o seu estado na base de dados para `PROCESSED`.

## Infraestrutura AWS

A infraestrutura é criada com Terraform e inclui:

* VPC
* Subnets públicas
* Subnets privadas
* Internet Gateway
* Route tables
* Security Groups
* EC2
* RDS PostgreSQL
* SQS Queue
* SQS Dead Letter Queue
* S3 Bucket para Terraform remote state
* DynamoDB Table para state locking
* ECR repositories para imagens Docker

## CI/CD

O projeto usa GitHub Actions.

O fluxo é:

```text
Pull Request
  └── Terraform fmt
  └── Terraform init
  └── Terraform validate
  └── Terraform plan
  └── Docker build dos serviços

Merge para main
  └── Terraform apply
  └── Docker build
  └── Push das imagens para AWS ECR
  └── Deploy na EC2 com Ansible
```

## Estrutura do projeto

```text
Project_Cloud/
│
├── services/
│   ├── api-gateway/
│   ├── order-service/
│   ├── worker-service/
│   └── hello-world/
│
├── terraform/
│   ├── versions.tf
│   ├── providers.tf
│   ├── variables.tf
│   ├── networking.tf
│   ├── compute.tf
│   ├── database.tf
│   ├── sqs.tf
│   ├── outputs.tf
│   └── main.tf
│
├── ansible/
│   ├── deploy-hello.yml
│   └── deploy-services.yml
│
├── .github/
│   └── workflows/
│       ├── hello-world-deploy.yml
│       ├── pr-checks.yml
│       └── deploy-production.yml
│
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   └── security.md
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

## Execução local

Para correr localmente:

```powershell
docker compose up --build
```

Testar o estado da API:

```powershell
curl.exe "http://localhost:8080/health"
```

Criar uma order:

```powershell
'{"product_name":"Laptop","quantity":1}' | Out-File -Encoding ascii body.json
curl.exe -X POST "http://localhost:8080/orders" -H "Content-Type: application/json" --data-binary "@body.json"
```

Listar orders:

```powershell
curl.exe "http://localhost:8080/orders"
```

## Deploy em produção

O deploy é feito automaticamente quando existe merge para a branch `main`.

O GitHub Actions:

1. Corre Terraform.
2. Faz build das imagens Docker.
3. Faz push para AWS ECR.
4. Usa Ansible para entrar na EC2.
5. Atualiza os containers em execução.

## Branches

O projeto usa duas branches principais:

```text
dev
main
```

A branch `dev` é usada para desenvolvimento.
A branch `main` representa a versão estável e é usada para deploy de produção.

O fluxo usado é:

```text
dev → Pull Request → main → Production Deploy
```

````

---

# `docs/architecture.md`

```markdown
# Arquitetura do Projeto

## Visão geral

Este projeto implementa uma aplicação cloud baseada em microserviços, alojada na AWS.

A infraestrutura é criada com Terraform, os serviços correm em containers Docker numa instância EC2, e o processo de deploy é automatizado com GitHub Actions e Ansible.

A aplicação é composta por três serviços principais:

- `api-gateway`
- `order-service`
- `worker-service`

O `api-gateway` recebe pedidos HTTP dos utilizadores. O `order-service` gere a criação e listagem de orders. O `worker-service` processa mensagens assíncronas vindas de uma fila SQS.

## Abordagem do projeto

Este projeto segue a abordagem de aplicação personalizada.

O objetivo principal não é criar uma aplicação de negócio complexa, mas sim demonstrar conceitos de engenharia cloud:

- Infrastructure as Code com Terraform
- Deploy automatizado
- Containers Docker
- CI/CD com GitHub Actions
- Comunicação assíncrona com SQS
- Base de dados privada com RDS
- Separação entre rede pública e privada
- Gestão de secrets e boas práticas de segurança

## Diagrama lógico

```text
Utilizador
   |
   v
Internet
   |
   v
EC2 - Public Subnet
   |
   |---- api-gateway
   |        |
   |        v
   |---- order-service
   |        |
   |        |---- RDS PostgreSQL - Private Subnet
   |        |
   |        v
   |---- SQS Queue
            |
            v
        worker-service
            |
            v
      Atualiza estado da order na RDS
````

## Diagrama de infraestrutura

```text
GitHub
  |
  v
GitHub Actions
  |
  |---- Terraform apply
  |---- Docker build
  |---- Push para AWS ECR
  |---- Ansible deploy
  |
  v
AWS
  |
  |---- VPC
  |      |
  |      |---- Public Subnets
  |      |       |
  |      |       └── EC2 com Docker
  |      |
  |      |---- Private Subnets
  |              |
  |              └── RDS PostgreSQL
  |
  |---- SQS Queue
  |---- SQS Dead Letter Queue
  |---- ECR Repositories
  |---- S3 Bucket para Terraform State
  |---- DynamoDB Table para Terraform Lock
```

## Componentes AWS

### VPC

A VPC isola a infraestrutura do projeto dentro da AWS. Dentro dela existem subnets públicas e privadas.

### Subnets públicas

As subnets públicas alojam a instância EC2, que precisa de acesso à internet para receber pedidos HTTP e para permitir deploy via SSH/Ansible.

### Subnets privadas

As subnets privadas alojam a base de dados RDS. A base de dados não está exposta diretamente à internet.

### EC2

A EC2 funciona como servidor da aplicação. Nela correm os containers Docker:

* `api-gateway`
* `order-service`
* `worker-service`

### RDS PostgreSQL

A base de dados PostgreSQL guarda as orders criadas pela aplicação.

A RDS está em subnets privadas e só aceita ligações vindas do Security Group da aplicação.

### SQS

A fila SQS permite comunicação assíncrona entre o `order-service` e o `worker-service`.

Quando uma order é criada, o `order-service` envia uma mensagem para a fila.

### Dead Letter Queue

A DLQ recebe mensagens que falham várias vezes no processamento. Isto melhora a resiliência do sistema.

### ECR

O Amazon ECR é usado para guardar as imagens Docker dos serviços:

* `tomber-api-gateway`
* `tomber-order-service`
* `tomber-worker-service`

### S3 e DynamoDB

O bucket S3 guarda o Terraform remote state.

A tabela DynamoDB é usada para state locking, evitando que duas execuções de Terraform alterem o estado ao mesmo tempo.

## Fluxo de dados

```text
1. O utilizador envia um pedido HTTP para o api-gateway.
2. O api-gateway encaminha o pedido para o order-service.
3. O order-service cria uma order na base de dados RDS.
4. O order-service envia uma mensagem para a fila SQS.
5. O worker-service consome a mensagem da fila SQS.
6. O worker-service processa a order.
7. O worker-service atualiza o estado da order para PROCESSED na RDS.
```

## Fluxo de deploy

```text
Developer
  |
  v
Branch dev
  |
  v
Pull Request para main
  |
  v
GitHub Actions - Pull Request Checks
  |
  |---- Terraform fmt
  |---- Terraform init
  |---- Terraform validate
  |---- Terraform plan
  |---- Docker build
  |
  v
Merge para main
  |
  v
GitHub Actions - Production Deploy
  |
  |---- Terraform apply
  |---- Build Docker images
  |---- Push para AWS ECR
  |---- Ansible deploy para EC2
  |
  v
Aplicação atualizada em produção
```

## Naming convention

Os recursos seguem o padrão:

```text
tomber-cloud-dev-resource-name
```

Exemplos:

```text
tomber-cloud-dev-vpc
tomber-cloud-dev-ec2-app
tomber-cloud-dev-postgres
tomber-cloud-dev-orders-queue
tomber-cloud-dev-orders-dlq
tomber-cloud-dev-sg-web
tomber-cloud-dev-sg-db
```

## Justificação da arquitetura

A arquitetura foi desenhada para demonstrar boas práticas cloud sem aumentar demasiado a complexidade.

A EC2 permite executar containers Docker de forma simples. A RDS garante persistência de dados. A SQS permite processamento assíncrono. O Terraform garante que a infraestrutura pode ser recriada. O GitHub Actions e o Ansible automatizam o processo de deploy.

```
```