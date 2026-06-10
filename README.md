# Cloud Microservices Project

Este projeto implementa uma aplicação distribuída e cloud-native alojada na AWS.

A arquitetura é inspirada no exemplo **Mini E-Commerce**, mas adaptada para um sistema simples de gestão e processamento de pedidos. O foco principal não é a complexidade da aplicação, mas sim a demonstração de boas práticas de engenharia cloud.

## Objetivo do Projeto

O projeto demonstra:

- Criação de infraestrutura na AWS
- Infraestrutura como código com Terraform
- Serviços containerizados com Docker
- Comunicação entre múltiplos serviços
- Comunicação assíncrona com AWS SQS
- Persistência de dados com AWS RDS
- Automação com Ansible
- Pipeline CI/CD com GitHub Actions
- Segurança com IAM, Security Groups e gestão segura de credenciais

## Componentes Principais

| Componente | Função |
|---|---|
| `api-gateway` | Serviço público que recebe pedidos HTTP |
| `order-service` | Serviço responsável pela lógica dos pedidos |
| `worker-service` | Serviço em background que consome mensagens da fila |
| `AWS SQS` | Fila usada para comunicação assíncrona |
| `AWS RDS` | Base de dados persistente |
| `EC2 + Docker` | Ambiente onde os containers correm |
| `Terraform` | Criação da infraestrutura AWS |
| `Ansible` | Configuração automática da instância EC2 |
| `GitHub Actions` | Automação de build, validação e deploy |

## Requisitos Obrigatórios Cumpridos

- Custom VPC
- Subnets públicas e/ou privadas
- Security Groups
- Route Tables
- Internet Gateway
- Infraestrutura criada com Terraform
- Serviços containerizados com Docker
- Arquitetura distribuída com múltiplos serviços
- Comunicação assíncrona com AWS SQS
- Base de dados persistente com AWS RDS
- Automação com Ansible
- Pipeline CI/CD com GitHub Actions
- Boas práticas de IAM e segurança

## Arquitetura Resumida

```text
Cliente
  |
  v
api-gateway
  |
  v
order-service
  |
  v
AWS SQS
  |
  v
worker-service
  |
  v
AWS RDS
```

## Como Executar Localmente

Na raiz do projeto:

```bash
docker compose up --build
```

Verificar containers:

```bash
docker ps
```

Testar endpoint de saúde:

```bash
curl http://localhost/health
```

## Como Fazer Deploy

O processo de deploy segue esta ordem:

```text
Terraform apply -> Build das imagens Docker -> Push das imagens -> Ansible deploy -> Aplicação em execução na EC2
```

## Documentação

A documentação completa está dividida nos seguintes ficheiros:

- [`docs/architecture.md`](docs/architecture.md)
- [`docs/setup.md`](docs/setup.md)
- [`docs/deployment.md`](docs/deployment.md)
- [`docs/security.md`](docs/security.md)
- [`docs/limitations.md`](docs/limitations.md)

## Stretch Goals Planeados

Foram escolhidos dois stretch goals:

1. **Health Checks**
    - Cada serviço expõe um endpoint `/health`.

2. **CloudWatch Logs**
    - Os logs dos containers são enviados para AWS CloudWatch Logs.

Estes objetivos melhoram a observabilidade, facilitam debugging e tornam a solução mais próxima de um ambiente real de produção.