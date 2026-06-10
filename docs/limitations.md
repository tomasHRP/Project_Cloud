# Limitações e Roadmap

Este documento descreve as limitações atuais do projeto e possíveis melhorias futuras.

## Limitações Atuais

O projeto foi desenvolvido com foco nos requisitos técnicos obrigatórios da unidade curricular.

A aplicação tem uma lógica de negócio simples, porque o objetivo principal é demonstrar conceitos de cloud engineering.

Limitações atuais:

- A aplicação tem uma interface mínima ou inexistente.
- O domínio de negócio é simples.
- O sistema corre em containers Docker dentro de uma EC2.
- Não existe ainda migração para ECS ou Fargate.
- Autoscaling não está implementado.
- Blue/Green ou Canary Deploys não estão implementados.
- Distributed tracing avançado não está implementado.
- Read replicas não estão implementadas.
- RDS Multi-AZ pode não estar ativo por razões de custo.
- Load testing é limitado.
- Secrets Manager ou SSM Parameter Store podem ainda não estar implementados.

## Limitações Técnicas

### Deploy em EC2

A aplicação é executada numa instância EC2 com Docker.

Esta abordagem cumpre os requisitos do projeto, mas em produção seria possível usar ECS, Fargate ou Kubernetes para melhor orquestração.

### Validação Manual

Algumas validações ainda podem ser feitas manualmente, como:

- Verificar endpoints com `curl`
- Consultar logs
- Verificar mensagens na SQS
- Confirmar dados na RDS

### Controlo de Custos

Algumas funcionalidades avançadas não foram implementadas para evitar custos adicionais na AWS.

Exemplos:

- RDS Multi-AZ
- Load Balancer
- Autoscaling Groups
- Read Replicas
- NAT Gateway

## Stretch Goals Planeados

Foram escolhidos dois stretch goals principais.

### Health Checks

Cada serviço irá expor um endpoint `/health`.

Isto permite verificar rapidamente se os serviços estão ativos.

Exemplo:

```bash
curl http://<EC2_PUBLIC_IP>/health
```

Resultado esperado:

```json
{
  "status": "ok"
}
```

### CloudWatch Logs

Os logs dos containers serão enviados para AWS CloudWatch Logs.

Cada serviço poderá ter o seu próprio log group:

```text
/cloud-project/api-gateway
/cloud-project/order-service
/cloud-project/worker-service
```

Isto melhora a observabilidade e facilita o debugging do fluxo distribuído:

```text
api-gateway -> order-service -> SQS -> worker-service -> RDS
```

## Roadmap Futuro

Melhorias possíveis:

- Implementar CloudWatch Logs
- Criar CloudWatch Metrics e Alarms
- Adicionar Dead Letter Queue à SQS
- Usar AWS Secrets Manager ou SSM Parameter Store
- Adicionar image scanning com Trivy
- Adicionar Terraform scanning com Checkov
- Implementar autoscaling do worker
- Adicionar Application Load Balancer
- Migrar para ECS/Fargate
- Implementar Blue/Green Deployments
- Criar dashboards de custos
- Implementar backups automáticos e estratégia de disaster recovery
- Adicionar documentação automática com `terraform-docs` ou OpenAPI

## Nota Final

O projeto dá prioridade aos requisitos obrigatórios.

Os stretch goals são implementados apenas depois da arquitetura base estar funcional, demonstrável e documentada.
