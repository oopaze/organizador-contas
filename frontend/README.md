# Bills Manager App

Um aplicativo moderno para controlar suas contas, despesas e receitas.

## Início Rápido (Modo Mock)

O app está configurado para rodar em **MODO MOCK** - sem necessidade de backend!

### 1. Instalar Dependências

```bash
npm install
```

### 2. Iniciar o Servidor de Desenvolvimento

```bash
npm run dev
```

### 3. Abrir no Navegador

Visite a URL mostrada no terminal (geralmente `http://localhost:5173`)

### 4. Login

Use as credenciais de demonstração:
- **Email**: `demo@example.com`
- **Password**: `password123`

Ou cadastre uma nova conta - qualquer email/senha funcionará no modo mock!

---

## Funcionalidades

- ✅ **Dashboard**: Visão geral das suas finanças com saldo, receitas e despesas
- ✅ **Adicionar Despesas**: Registre despesas individuais com fornecedores, valores e parcelas
- ✅ **Adicionar Receitas**: Registre receitas de várias fontes
- ✅ **Gerenciamento de Transações**: Visualize, filtre e exclua transações
- ✅ **Filtro por Mês/Ano**: Veja receitas e despesas de um período específico
- ✅ **Gerenciamento de Fornecedores**: Crie e gerencie fornecedores dinamicamente
- ✅ **Design Responsivo**: Funciona em desktop e mobile

---

## Alternar para Backend Real

Quando estiver pronto para conectar ao seu backend real:

1. **Abrir** `/src/services/client.ts`
2. **Mudar** linha 4 de:
   ```typescript
   export const USE_MOCK_API = true;
   ```
   para:
   ```typescript
   export const USE_MOCK_API = false;
   ```

3. **Atualizar** seu arquivo `.env` com a URL do backend:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

4. **Reiniciar** o servidor de desenvolvimento

---

## Dados Mock Incluídos

A API mock inclui dados de amostra:
- 2 transações de receita
- 6 despesas (mercado, assinaturas, combustível, jantar)
- 5 fornecedores predefinidos (Amazon, Netflix, Supermercado, etc.)
- Conta de usuário de demonstração

---

## Estrutura do Projeto

```
src/
├── app/
│   ├── components/
│   │   ├── LoginPage.tsx                # Página de Login/Cadastro
│   │   ├── Dashboard.tsx                # Painel principal
│   │   ├── TransactionsList.tsx         # Componente de lista de transações
│   │   ├── AddTransactionDialog.tsx     # Diálogo de adicionar receita
│   │   └── AddSubTransactionDialog.tsx  # Diálogo de adicionar despesa
│   └── App.tsx                          # Componente principal do app
├── contexts/
│   └── AuthContext.tsx                  # Contexto de autenticação
├── services/
│   ├── index.ts                         # Arquivo de exportação central
│   ├── types.ts                         # Tipos TypeScript compartilhados
│   ├── client.ts                        # Cliente API (toggle mock)
│   ├── mockData.ts                      # Armazenamento de dados mock
│   ├── auth/                            # Endpoints de autenticação
│   │   ├── login.ts
│   │   ├── register.ts
│   │   └── refresh.ts
│   ├── user/                            # Endpoints de usuário
│   │   ├── getCurrentUser.ts
│   │   └── updateProfile.ts
│   ├── transactions/                    # Endpoints de transação
│   │   ├── getTransactions.ts
│   │   ├── getTransaction.ts
│   │   ├── createTransaction.ts
│   │   ├── updateTransaction.ts
│   │   └── deleteTransaction.ts
│   ├── subTransactions/                 # Endpoints de sub-transação
│   │   ├── getSubTransactions.ts
│   │   ├── getSubTransaction.ts
│   │   ├── createSubTransaction.ts
│   │   ├── updateSubTransaction.ts
│   │   └── deleteSubTransaction.ts
│   ├── actors/                          # Endpoints de ator (fornecedor)
│   │   ├── getActors.ts
│   │   ├── getActor.ts
│   │   ├── createActor.ts
│   │   ├── updateActor.ts
│   │   └── deleteActor.ts
│   └── bills/                           # Endpoints de conta
│       ├── getBills.ts
│       ├── getBill.ts
│       └── uploadBill.ts
└── styles/
```

## Arquitetura de Serviços

O app segue uma **arquitetura de serviços modular** que espelha a estrutura do seu backend:

- **Um pedido por arquivo** - Cada endpoint da API tem seu próprio arquivo
- **Nomenclatura consistente** - Arquivos nomeados após a função que exportam
- **Cliente único** - Cliente API compartilhado em `client.ts` com toggle mock
- **Importações fáceis** - Importe tudo de `@/services`

Exemplo:
```typescript
import { login, getTransactions, createActor } from '@/services';
```

---

## Stack Tecnológica

- **React 18** com TypeScript
- **Tailwind CSS v4** para estilização
- **Radix UI** para componentes acessíveis
- **Vite** para ferramentas de construção
- **React Hook Form** para gerenciamento de formulários
- **Sonner** para notificações de toast

---

## Precisa de Ajuda?

- Todos os dados no modo mock são armazenados na memória e serão resetados ao atualizar
- No modo real, certifique-se de que as configurações CORS do seu backend permitam `http://localhost:5173`
- Verifique o console do navegador para quaisquer mensagens de erro