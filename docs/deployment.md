# Deployment

Este documento explica o processo de deploy da aplicação na AWS.

## Visão Geral do Deploy

O processo de deploy segue esta sequência:

```text
1. Criar infraestrutura com Terraform
2. Gerar imagens Docker
3. Publicar imagens num container registry
4. Configurar a EC2 com Ansible
5. Executar containers na EC2
6. Validar a aplicação
```

## Passo 1 — Criar Infraestrutura com Terraform

Entrar na pasta da infraestrutura:

```bash
cd infra
```

Inicializar Terraform:

```bash
terraform init
```

Validar o plano:

```bash
terraform plan
```

Aplicar a infraestrutura:

```bash
terraform apply
```

O Terraform cria recursos como:

- Custom VPC
- Subnets públicas e/ou privadas
- Route Tables
- Internet Gateway
- Security Groups
- EC2
- RDS
- SQS
- IAM Roles e Policies

## Passo 2 — Gerar Imagens Docker

Cada serviço tem o seu próprio Dockerfile.

Exemplo:

```bash
docker build -t api-gateway ./services/api-gateway
docker build -t order-service ./services/order-service
docker build -t worker-service ./services/worker-service
```

## Passo 3 — Publicar Imagens num Registry

As imagens podem ser publicadas em Docker Hub, GitHub Container Registry ou AWS ECR.

Exemplo genérico:

```bash
docker tag api-gateway <registry>/api-gateway:latest
docker tag order-service <registry>/order-service:latest
docker tag worker-service <registry>/worker-service:latest

docker push <registry>/api-gateway:latest
docker push <registry>/order-service:latest
docker push <registry>/worker-service:latest
```

## Passo 4 — Configurar EC2 com Ansible

O Ansible é usado para configurar automaticamente a instância EC2.

Tarefas típicas:

- Instalar Docker
- Instalar Docker Compose
- Copiar ficheiros de deploy
- Criar ficheiro `.env`
- Fazer pull das imagens Docker
- Iniciar os containers

Executar o playbook:

```bash
cd ansible
ansible-playbook -i inventory.ini playbook.yml
```

## Passo 5 — Iniciar a Aplicação

Na EC2, os containers são iniciados com:

```bash
docker compose up -d
```

Verificar containers:

```bash
docker ps
```

Verificar logs:

```bash
docker logs api-gateway
docker logs order-service
docker logs worker-service
```

## Passo 6 — Validar o Deploy

Testar o endpoint público:

```bash
curl http://<EC2_PUBLIC_IP>/health
```

Resultado esperado:

```json
{
  "status": "ok"
}
```

Validar também o fluxo principal:

```text
Cliente -> api-gateway -> order-service -> SQS -> worker-service -> RDS
```

## GitHub Actions

O projeto usa GitHub Actions para automatizar o processo de CI/CD.

O workflow deve estar em:

```text
.github/workflows/deploy.yml
```

O pipeline pode incluir:

- Checkout do código
- Build das imagens Docker
- Push das imagens para o registry
- Validação de Terraform
- Deploy para EC2 através de Ansible ou SSH

## Evidências de Deploy

Para a apresentação ou relatório, devem ser recolhidas evidências como:

- Output do `terraform apply`
- Recursos criados na AWS
- VPC, Subnets e Security Groups
- EC2 em execução
- RDS ativo
- SQS criada
- Containers em execução na EC2
- Workflow do GitHub Actions concluído com sucesso
- Endpoint público a responder
