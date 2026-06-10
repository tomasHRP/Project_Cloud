# Arquitetura

## Visão Geral

Este projeto segue uma arquitetura distribuída baseada em microserviços.

A aplicação é composta por vários serviços independentes que comunicam entre si através de HTTP e através de comunicação assíncrona com AWS SQS.

A solução está alojada na AWS e utiliza uma infraestrutura criada com Terraform.

## Diagrama da Arquitetura

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
AWS SQS Queue
  |
  v
worker-service
  |
  v
AWS RDS Database
```

## Infraestrutura AWS

A infraestrutura é criada dentro de uma VPC própria.

```text
AWS
└── Custom VPC
    ├── Public Subnet
    │   └── EC2 com Docker
    ├── Private Subnet
    │   └── RDS Database
    ├── Route Tables
    ├── Internet Gateway
    └── Security Groups
```

## Componentes da Aplicação

### api-gateway

O `api-gateway` é o serviço exposto publicamente.

Responsabilidades:

- Receber pedidos HTTP do cliente
- Encaminhar pedidos para o `order-service`
- Expor endpoints públicos
- Disponibilizar endpoint `/health`

Este serviço representa a entrada principal da aplicação.

### order-service

O `order-service` contém a lógica principal relacionada com pedidos.

Responsabilidades:

- Receber pedidos vindos do `api-gateway`
- Criar eventos relacionados com pedidos
- Publicar mensagens na fila AWS SQS
- Comunicar com a base de dados quando necessário
- Disponibilizar endpoint `/health`

Este serviço atua como produtor de mensagens para a fila SQS.

### worker-service

O `worker-service` é um serviço de background.

Responsabilidades:

- Consumir mensagens da AWS SQS
- Processar tarefas de forma assíncrona
- Guardar ou atualizar dados na base de dados RDS
- Produzir logs sobre o processamento das mensagens

Este serviço atua como consumidor da fila SQS.

## Comunicação entre Serviços

O projeto demonstra dois tipos de comunicação.

### Comunicação Síncrona

A comunicação síncrona acontece através de HTTP.

Exemplo:

```text
api-gateway -> order-service
```

### Comunicação Assíncrona

A comunicação assíncrona acontece através de AWS SQS.

Exemplo:

```text
order-service -> SQS -> worker-service
```

Esta abordagem permite desacoplar os serviços. O `order-service` não precisa de esperar que o `worker-service` processe a tarefa imediatamente.

## AWS SQS

A AWS SQS é usada como mecanismo de comunicação assíncrona.

Vantagens:

- Desacoplamento entre serviços
- Processamento em background
- Maior tolerância a falhas
- Possibilidade de retry
- Possibilidade de Dead Letter Queue

Produtor:

```text
order-service
```

Consumidor:

```text
worker-service
```

## AWS RDS

A AWS RDS é usada como camada de persistência.

A base de dados guarda informação da aplicação, como pedidos ou resultados processados.

Idealmente, a base de dados deve estar numa subnet privada e apenas acessível pela EC2 ou pelos serviços autorizados.

## Fluxo de Dados

1. O cliente faz um pedido ao `api-gateway`.
2. O `api-gateway` encaminha o pedido para o `order-service`.
3. O `order-service` cria um evento e envia uma mensagem para a AWS SQS.
4. O `worker-service` lê a mensagem da fila.
5. O `worker-service` processa a mensagem.
6. O resultado é guardado ou atualizado na base de dados RDS.

## Objetivo Técnico

O foco do projeto não é a complexidade da aplicação, mas sim a qualidade da engenharia cloud.

O projeto demonstra:

- Separação de serviços
- Comunicação entre serviços
- Comunicação assíncrona
- Infraestrutura isolada em VPC
- Uso de base de dados persistente
- Automação da infraestrutura
- Automação do deploy
- Segurança com IAM e Security Groups
- Observabilidade através de logs e health checks
