# Segurança

Este documento descreve as decisões de segurança aplicadas no projeto.

## IAM

O projeto deve seguir o princípio de menor privilégio.

Isto significa que cada componente deve ter apenas as permissões necessárias para cumprir a sua função.

Exemplos:

- A EC2 deve ter apenas permissões necessárias para aceder aos serviços usados pela aplicação.
- O acesso à SQS deve ser limitado à fila usada no projeto.
- O acesso ao CloudWatch Logs deve ser limitado aos log groups necessários.
- O GitHub Actions deve usar permissões controladas para fazer deploy.
- As permissões não devem usar `*` quando for possível definir recursos específicos.

## Gestão de Credenciais

Informação sensível não deve estar escrita diretamente no código.

São considerados dados sensíveis:

- AWS Access Key ID
- AWS Secret Access Key
- Password da base de dados
- Chaves privadas SSH
- Tokens de acesso
- API keys

Estes valores devem ser guardados usando:

- GitHub Secrets
- Variáveis de ambiente
- Ficheiros `.env` não versionados
- AWS SSM Parameter Store ou Secrets Manager, caso implementado

## Ficheiros a Ignorar

O `.gitignore` deve incluir:

```gitignore
.env
*.pem
terraform.tfstate
terraform.tfstate.backup
.terraform/
```

Isto evita que credenciais, chaves privadas e ficheiros sensíveis do Terraform sejam enviados para o GitHub.

## Segurança de Rede

A infraestrutura usa uma VPC personalizada e Security Groups para controlar o tráfego.

### Security Group da EC2

Regras recomendadas de entrada:

```text
HTTP 80  -> aberto ao público
SSH 22   -> apenas para o IP do programador
```

Regras de saída:

```text
Permitir tráfego necessário para comunicar com RDS, SQS, internet e updates do sistema
```

### Security Group da RDS

A base de dados não deve estar aberta ao público.

Regras recomendadas:

```text
PostgreSQL 5432 ou MySQL 3306 -> permitido apenas a partir da EC2
```

Isto impede acessos diretos externos à base de dados.

## Segurança da Base de Dados

A base de dados RDS deve:

- Não estar publicamente acessível
- Estar protegida por Security Group
- Usar credenciais fora do código
- Ser acedida apenas pelos serviços autorizados

## Segurança da SQS

A fila SQS deve ser acedida apenas pelos serviços necessários.

Exemplo:

- `order-service` pode enviar mensagens
- `worker-service` pode receber e apagar mensagens

As permissões devem ser configuradas com IAM.

## Segurança no CI/CD

O GitHub Actions deve usar GitHub Secrets para dados sensíveis.

Exemplos de secrets:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
EC2_HOST
EC2_USER
EC2_SSH_KEY
DB_PASSWORD
```

Sempre que possível, deve ser usado OIDC para evitar chaves AWS fixas.

## Evidências de Segurança

Durante a apresentação, podem ser mostradas as seguintes evidências:

- Security Groups na AWS
- RDS sem acesso público
- IAM Role associada à EC2
- GitHub Secrets configurados
- Código sem passwords hardcoded
- `.gitignore` com ficheiros sensíveis ignorados
- Permissões IAM com menor privilégio possível
