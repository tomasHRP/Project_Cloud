# Arquitetura

## Abordagem do Projeto

Este projeto segue a **Approach B — Custom Application Track**.

A aplicação foi desenvolvida como um sistema simples de microserviços, com o objetivo de demonstrar conceitos fundamentais de Cloud Engineering, incluindo automação de infraestrutura, deploy com containers, CI/CD, comunicação assíncrona, integração com base de dados e boas práticas de segurança.

O objetivo principal do projeto não é criar uma aplicação de negócio complexa, mas sim demonstrar a utilização correta de AWS, Terraform, Docker, Ansible, GitHub Actions, Amazon RDS, Amazon SQS e Amazon ECR numa arquitetura cloud-native.

## Visão Geral

Este projeto consiste numa aplicação de microserviços alojada na AWS.

A aplicação corre em containers Docker numa instância EC2. A infraestrutura é criada através de Terraform, enquanto o deploy é automatizado com GitHub Actions e Ansible.

O sistema é composto por três serviços principais:

* `api-gateway`
* `order-service`
* `worker-service`

O `api-gateway` é o ponto de entrada público da aplicação. Recebe pedidos HTTP dos utilizadores e encaminha-os para o `order-service`.

O `order-service` é responsável por criar e listar orders. Sempre que uma nova order é criada, os dados são guardados numa base de dados PostgreSQL em Amazon RDS e é enviada uma mensagem para uma fila Amazon SQS.

O `worker-service` consome mensagens da fila SQS e processa as orders de forma assíncrona, atualizando o seu estado na base de dados para `PROCESSED`.

## Diagrama da Arquitetura

```text
Utilizador
   |
   v
Internet
   |
   v
EC2 Instance - Public Subnet
   |
   |---- api-gateway
   |        |
   |        v
   |---- order-service
   |        |
   |        |---- Amazon RDS PostgreSQL - Private Subnet
   |        |
   |        v
   |---- Amazon SQS Queue
            |
            v
        worker-service
            |
            v
      Atualiza estado da order na RDS
```

## Diagrama de Infraestrutura e Deploy

```text
Developer
   |
   v
GitHub
   |
   v
GitHub Actions
   |
   |---- Terraform apply
   |---- Docker build
   |---- Push para Amazon ECR
   |---- Deploy com Ansible
   |
   v
AWS
   |
   |---- VPC
   |     |
   |     |---- Public Subnets
   |     |       |
   |     |       └── EC2 com Docker
   |     |
   |     |---- Private Subnets
   |             |
   |             └── Amazon RDS PostgreSQL
   |
   |---- Amazon SQS Queue
   |---- Amazon SQS Dead Letter Queue
   |---- Amazon ECR Repositories
   |---- S3 Bucket para Terraform Remote State
   |---- DynamoDB Table para Terraform State Locking
```

## Infraestrutura AWS

O projeto foi implementado na região:

```text
us-east-1
```

A infraestrutura inclui:

* VPC
* Public subnets
* Private subnets
* Internet Gateway
* Route tables
* Security Groups
* EC2 instance
* Amazon RDS PostgreSQL
* Amazon SQS Queue
* Amazon SQS Dead Letter Queue
* Amazon ECR repositories
* S3 Bucket para Terraform remote state
* DynamoDB Table para Terraform state locking

## Componentes da Arquitetura

### VPC

A VPC isola os recursos do projeto dentro da AWS. Esta rede contém subnets públicas e privadas, permitindo separar os recursos acessíveis pela internet dos recursos internos.

### Public Subnets

As public subnets alojam a instância EC2. A EC2 precisa de estar numa subnet pública porque recebe tráfego HTTP dos utilizadores e também é usada no processo de deploy através de SSH/Ansible.

### Private Subnets

As private subnets alojam a base de dados Amazon RDS. A base de dados não está exposta diretamente à internet, aumentando a segurança da solução.

### EC2 Instance

A EC2 funciona como servidor da aplicação. Nesta instância correm os containers Docker dos três serviços principais:

* `api-gateway`
* `order-service`
* `worker-service`

### Amazon RDS PostgreSQL

O Amazon RDS PostgreSQL é usado para guardar os dados das orders.

A base de dados está configurada como privada, ou seja, não está publicamente acessível. Apenas os serviços da aplicação conseguem comunicar com a RDS através dos Security Groups definidos.

### Amazon SQS

O Amazon SQS é usado para comunicação assíncrona entre o `order-service` e o `worker-service`.

Quando uma order é criada, o `order-service` envia uma mensagem para a fila SQS. O `worker-service` consome essa mensagem e processa a order em background.

### Dead Letter Queue

A Dead Letter Queue recebe mensagens que falham várias vezes no processamento. Isto permite isolar mensagens problemáticas e melhora a resiliência da aplicação.

### Amazon ECR

O Amazon ECR é usado como registry privado para guardar as imagens Docker dos serviços.

Foram usados três repositórios ECR:

```text
tomber-api-gateway
tomber-order-service
tomber-worker-service
```

Durante o deploy, o GitHub Actions faz build das imagens, envia-as para o ECR e depois a EC2 faz pull dessas imagens.

### S3 e DynamoDB

O S3 Bucket é usado para guardar o Terraform remote state.

A DynamoDB Table é usada para Terraform state locking. Isto evita que duas execuções de Terraform modifiquem a infraestrutura ao mesmo tempo.

## Limites dos Serviços

### api-gateway

O `api-gateway` é o ponto de entrada público da aplicação.

Responsabilidades:

* Receber pedidos HTTP dos utilizadores.
* Expor os endpoints principais da aplicação.
* Encaminhar pedidos para o `order-service`.

Endpoints principais:

```text
GET /health
POST /orders
GET /orders
```

### order-service

O `order-service` é responsável pela lógica principal relacionada com orders.

Responsabilidades:

* Criar orders.
* Guardar orders na base de dados PostgreSQL.
* Listar orders existentes.
* Enviar mensagens para a fila SQS quando uma order é criada.

### worker-service

O `worker-service` processa tarefas em background.

Responsabilidades:

* Consumir mensagens da fila SQS.
* Processar orders de forma assíncrona.
* Atualizar o estado das orders para `PROCESSED`.
* Garantir que o processamento não bloqueia o pedido principal do utilizador.

## Fluxo de Dados

```text
1. O utilizador envia um pedido HTTP para o api-gateway.
2. O api-gateway encaminha o pedido para o order-service.
3. O order-service cria a order na base de dados RDS PostgreSQL.
4. O order-service envia uma mensagem para a fila Amazon SQS.
5. O worker-service consome a mensagem da fila SQS.
6. O worker-service processa a order.
7. O worker-service atualiza o estado da order na base de dados para PROCESSED.
8. O utilizador pode consultar a lista de orders através do api-gateway.
```

## Fluxo de Deploy

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
   |---- Login no Amazon ECR
   |---- Docker build
   |---- Push das imagens para Amazon ECR
   |---- Deploy na EC2 com Ansible
   |
   v
Aplicação atualizada em produção
```

## Estratégia de Branches

O projeto usa duas branches principais:

```text
main
dev
```

A branch `dev` é usada para desenvolvimento.

A branch `main` representa a versão estável do projeto e é usada para deploy de produção.

O fluxo usado é:

```text
dev → Pull Request → main → Production Deploy
```

A branch `main` deve ser protegida para evitar alterações diretas sem validação.

## Naming Convention

Os recursos AWS usam o seguinte padrão de nomes:

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

Este padrão facilita a identificação dos recursos na AWS e mantém consistência entre os diferentes componentes da infraestrutura.

## Escolhas Tecnológicas

| Área                   | Tecnologia            |
| ---------------------- | --------------------- |
| Cloud Provider         | AWS                   |
| Região                 | us-east-1             |
| Infrastructure as Code | Terraform             |
| Deploy                 | Ansible               |
| CI/CD                  | GitHub Actions        |
| Compute                | EC2                   |
| Containers             | Docker                |
| Container Registry     | Amazon ECR            |
| Base de dados          | Amazon RDS PostgreSQL |
| Queue                  | Amazon SQS            |
| Remote State           | S3                    |
| State Locking          | DynamoDB              |
| Version Control        | GitHub                |
| Linguagem da aplicação | Python Flask          |

## Justificação da Arquitetura

A arquitetura foi escolhida para demonstrar os principais conceitos de uma solução cloud moderna, mantendo a complexidade controlada.

A EC2 permite executar os containers Docker de forma simples. O Amazon RDS garante persistência de dados. O Amazon SQS permite processamento assíncrono. O Amazon ECR permite guardar imagens Docker de forma segura. O Terraform permite criar e gerir a infraestrutura como código. O GitHub Actions automatiza o pipeline CI/CD. O Ansible automatiza o deploy dos serviços na EC2.

Esta arquitetura demonstra uma solução completa, desde a criação da infraestrutura até ao deploy automatizado da aplicação.