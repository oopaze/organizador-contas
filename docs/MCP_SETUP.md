# MCP Poupix — Setup local

Este guia configura o servidor MCP do Poupix para uso com Claude Desktop ou Claude Code.

## Pré-requisitos

- Banco e Redis rodando (`docker compose -f docker-compose.api.yml up -d db redis`).
- Backend Python instalado (`pip install -r backend/requirements.txt`).
- Migrations aplicadas (`make migrate`).

## 1. Criar o role read-only no Postgres

```bash
# Gere uma senha forte
export MCP_DATABASE_PASSWORD=$(openssl rand -hex 16)
echo "MCP_DATABASE_PASSWORD=$MCP_DATABASE_PASSWORD" >> backend/.env

# Crie o role no banco (precisa do password de superuser do PG)
PG_ADMIN_PASSWORD=postgres make mcp_setup_db
```

No Windows (PowerShell):

```powershell
$pw = -join ((48..57) + (97..122) | Get-Random -Count 32 | % { [char]$_ })
Add-Content backend/.env "MCP_DATABASE_PASSWORD=$pw"
$env:PG_ADMIN_PASSWORD = "postgres"
make mcp_setup_db
```

Saída esperada: `Role poupix_mcp_ro created/reset with SELECT-only privileges.`

## 2. Descobrir seu user_id

```bash
cd backend
python manage.py mcp_whoami seu-email@exemplo.com
```

Saída: `user_id = 7  (use this as POUPIX_MCP_USER_ID)`. Anote esse número.

## 3. Configurar o cliente MCP

### Claude Desktop

Abra `%APPDATA%\Claude\claude_desktop_config.json` (Windows) ou `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac) e adicione:

```json
{
  "mcpServers": {
    "poupix": {
      "command": "python",
      "args": ["manage.py", "run_mcp"],
      "cwd": "C:/Users/Pedro/Documents/projtos/organizador-contas-main/backend",
      "env": {
        "POUPIX_MCP_USER_ID": "7"
      }
    }
  }
}
```

Substitua `cwd` pelo caminho absoluto do seu repositório, e `POUPIX_MCP_USER_ID` pelo seu user_id.

### Claude Code

Edite `~/.claude/mcp.json` (ou onde sua instalação espera) com o mesmo bloco acima.

## 4. Reiniciar o cliente MCP e testar

Reinicie Claude Desktop / Claude Code. Em uma conversa nova, peça:

> "Quais foram minhas 5 maiores despesas dos últimos 30 dias?"

O agente deve usar `list_enums` e/ou `describe_schema` para se orientar e depois compor uma query `execute_sql`.

## Ferramentas expostas

| Tool | Parâmetros | O que faz |
|---|---|---|
| `execute_sql` | `query: string` | Executa SELECT read-only. Escopo automático ao seu usuário, soft-deleted excluídos, limite de 1000 linhas, timeout de 5s. |
| `describe_schema` | `table: string?` | Lista tabelas e colunas. Sem parâmetro = todas; com table = detalhe. |
| `list_enums` | — | Retorna slugs/labels válidos para `category` e `transaction_type`. |

## Segurança

O servidor é seguro em três camadas:

1. **Role Postgres `poupix_mcp_ro`** — `GRANT SELECT` apenas. Qualquer DDL/DML é bloqueado pelo banco, mesmo que o validador SQL tenha bug.
2. **Sessão read-only** — toda conexão abre em modo read-only com `statement_timeout=5s`.
3. **Validador SQL** — rejeita statements não-SELECT antes de chegar no banco (UX, não segurança).

Toda query é envolta em CTEs que sombram nomes de tabela com versões filtradas por `user_id` e `deleted_at IS NULL`, então é impossível para o agente "esquecer" o filtro.

## Troubleshooting

- **`FATAL: role "poupix_mcp_ro" does not exist`** — rode o passo 1.
- **`POUPIX_MCP_USER_ID is required`** — o cliente MCP não exportou a variável; verifique o `env` no bloco do `mcp.json`.
- **`SQL_TIMEOUT` em queries simples** — o banco pode estar sob carga; tente filtrar mais agressivamente ou agregue.
