# Poupix como app instalável (PWA) — Design Spec

**Data:** 2026-09-09
**Status:** Aguardando revisão do usuário

## Objetivo

Transformar o frontend web existente num app instalável na tela inicial do celular, sem reescrever a UI. O app instalado esconde as telas de AI/MCP e navega por uma barra de abas embaixo. Nenhuma funcionalidade de dinheiro é removida.

O pedido original mencionava React Native. Foi descartado na fase de brainstorming: o custo era reescrever a UI inteira (Radix, Tailwind, Recharts e react-router não existem em React Native), e a decisão do usuário foi PWA sobre o web atual.

## Decisões de design

1. **PWA, não React Native** — a UI atual é reaproveitada por inteiro. O trabalho vira aditivo (manifest, service worker, ícones) em vez de uma segunda base de código. Sem loja de apps, sem push no iOS, sem câmera nativa — aceito.
2. **Offline só da casca** — o service worker faz precache dos assets do build. Sem internet o app abre e as telas montam; os dados falham com erro de rede. Não há cache de respostas da API. Motivo: dado financeiro velho exibido sem aviso é pior que erro honesto, e cache de API traz invalidação como problema próprio.
3. **Esconder AI/MCP, não deletar** — `/chat`, `/ai-insights` e `/integrations` somem do menu quando `display-mode: standalone`. Continuam no código, nas rotas e acessíveis pelo navegador. Reversível por uma linha.
4. **Barra de abas embaixo em vez do menu no topo** — três destinos (Início, Empréstimos, Atores) na altura do polegar, com rótulo em texto. Hoje os ícones são rotulados só por `title=`, que não existe em toque.
5. **Tabelas ficam como estão** — elas já rolam horizontalmente (`ui/table.tsx` envolve toda tabela num `overflow-x-auto`). São desconfortáveis no celular, não quebradas. Reescrevê-las como lista de cards seria código novo em 7 arquivos sem nenhum padrão existente para copiar. Adiado para depois de uso real no celular.
6. **Alvos de toque e rótulos entram no escopo** — não é polimento. Hoje há ações destrutivas de 32px, coladas nas vizinhas, rotuladas só por tooltip que nunca aparece em toque.
7. **Popovers artesanais são substituídos, não corrigidos** — três reimplementações de posicionamento fixo sem clamp de viewport. O Radix `DropdownMenu` já é dependência e resolve. É remoção de código.

## Contexto verificado

Levantado por auditoria em paralelo com fase adversarial de confirmação: **54 achados confirmados, 12 refutados** em 9 clusters. Os refutados foram descartados e não constam deste spec.

### O que já está pronto

- Produção em HTTPS com Let's Encrypt: `https://poupix.connectakit.com.br`
- nginx já faz fallback de SPA (`try_files $uri $uri/ /index.html`)
- Vite sem `base` configurado — resolve para `/`, correto para service worker no escopo raiz
- `ui/table.tsx` já envolve toda tabela em `overflow-x-auto`
- Inputs em `text-base md:text-sm` — abaixo de 768px renderizam a 16px, então o iOS **não** dá zoom ao focar. Uma exceção conhecida, tratada em D3: `share-actor-dialog.tsx:108` sobrescreve com `text-sm`.

### O que não existe hoje

- Nenhum manifest, nenhum service worker, nenhuma dependência PWA/workbox
- Único ícone no repositório: `frontend/public/favicon.svg`. Nenhum PNG, nenhum apple-touch-icon
- Nenhum `env(safe-area-inset-*)` em `src/` ou `index.html`

### Acoplamento das telas de AI

Verificado por grep na árvore inteira: os únicos importadores de `services/chat` são `services/index.ts` e `chat-page.tsx`; de `services/ai`, `services/index.ts` e `ai-insights-page.tsx`; de `services/mcp`, apenas `integrations-page.tsx` e `oauth-authorize-page.tsx`. Nenhuma funcionalidade não-AI importa qualquer uma dessas páginas ou serviços.

Os uploads que usam AI no backend (fatura, planilha, comprovante PIX, adivinhar categoria) são independentes: cada diálogo declara sua própria lista de modelos e não importa nada de `services/chat`. **Continuam funcionando normalmente.**

## Arquitetura

### A. Tornar instalável

| Item | Arquivo |
|---|---|
| `vite-plugin-pwa` com `registerType: 'autoUpdate'` | `frontend/vite.config.ts` |
| `registerSW({ immediate: true })` | `frontend/src/main.tsx` |
| Manifest | `frontend/public/manifest.webmanifest` |
| Ícones PNG | `frontend/public/` |
| Tags de head | `frontend/index.html` |
| Exceção de cache | as **duas** configs nginx |

**Manifest:** `name` e `short_name` "Poupix", `start_url: "/"`, `scope: "/"`, `display: "standalone"`, `lang: "pt-BR"`, `theme_color` e `background_color` em esmeralda.

**Ícones** — gerados do `favicon.svg` existente com `qlmanage` (built-in do macOS, verificado: renderiza PNG 512×512 limpo). Nenhuma dependência nova, nenhum trabalho de design.

- `icon-192.png`, `icon-512.png` — `purpose: "any"`
- `icon-maskable-512.png` — `purpose: "maskable"`, com o gradiente **preenchendo o quadrado inteiro**. O SVG atual é um círculo que encosta na borda; sob a máscara squircle do Android os cantos ficariam transparentes.
- `apple-touch-icon.png` 180×180, **opaco** — o iOS não compõe alpha.

**Head do `index.html`:**

```html
<html lang="pt-BR">                                       <!-- hoje: "en" -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="format-detection" content="telephone=no">
<meta name="theme-color" content="#059669">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

**Cor de marca:** o ícone é índigo (`#4f46e5`), mas o header do app é `bg-emerald-600` e o login é gradiente esmeralda→teal. O ícone é o elemento fora do tom. O gradiente do SVG passa a esmeralda antes de gerar os PNGs, e `theme_color` acompanha.

**Exceção de cache — obrigatória.** O nginx dentro do `Dockerfile.frontend` cacheia por extensão:

```
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

`sw.js` termina em `.js`. Sem exceção, o service worker fica imutável por um ano e quem instalar **nunca mais recebe atualização** — irreversível do lado do servidor. Precisa de um `location = /sw.js` com `no-cache` acima da regra de extensão, e o mesmo para `index.html`.

O repositório tem **duas** configs nginx divergentes e contraditórias: `nginx/poupix-frontend.conf` (serve `/var/www/poupix` com TLS) e a embutida por heredoc no `Dockerfile.frontend` (usada por `docker-compose.prod.yml`, que é o que `deploy-hostinger.sh` sobe). Não é possível determinar pelo repositório qual está no ar. **A correção vai nas duas** — custa 4 linhas, menos que investigar.

### B. Esconder AI/MCP no app instalado

Hook novo:

```ts
// detecta o app instalado, não o tamanho da tela
matchMedia('(display-mode: standalone)').matches
  || (navigator as any).standalone === true   // iOS Safari legado
```

`layout.tsx` filtra três itens de nav quando verdadeiro. As rotas em `routes.tsx` não mudam.

`/oauth/authorize` não está no menu — é alvo de redirect vindo do Claude Desktop / ChatGPT, um fluxo que acontece no desktop. Escondê-la não tem efeito prático e não será feito.

### C. Barra de abas embaixo

Componente novo, três abas com ícone + rótulo em texto:

| Aba | Rota | Ícone atual |
|---|---|---|
| Início | `/` | `Home` |
| Empréstimos | `/loans` | `HandCoins` |
| Atores | `/actors` | `Users` |

Fixa embaixo, com `pb-[env(safe-area-inset-bottom)]`. O header fica com logo e sair. O `<main>` ganha padding inferior equivalente à altura da barra para o último item da lista não ficar embaixo dela.

`viewport-fit=cover` é necessário **por causa** desta seção. Registrado explicitamente: sem barra embaixo, o modo `contain` padrão do iOS já mantém o conteúdo fora do notch — a safe-area não é um bug preexistente.

O usuário escolheu abas embaixo sem restringir a celular; no desktop a barra também aparece. Se incomodar, vira `sm:hidden` com o menu do topo de volta acima de 640px — uma condição.

### D. Correções de celular

**D1 — Alvos de toque e rótulos.** Ações destrutivas passam a 44px e ganham `aria-label`:

- `loans-page.tsx:247-278` — cinco controles sem `gap`, 32px, rotulados só por `title=`. Um apaga o empréstimo e todos os pagamentos.
- `loans-page.tsx:235` — o chevron de expandir é `size="sm"` e é o único caminho até os pagamentos.
- `actors-page.tsx:436-460` — três botões `h-8 w-8` com `gap-1`; editar e apagar vizinhos; sem `aria-label`.
- `loan-payments-table.tsx:62` — apagar pagamento, sem `title` e sem `aria-label`.
- `actor-sub-transactions-table.tsx:208` e `transactions-list.tsx` — mesmo padrão.
- `ui/dialog.tsx:66` — o X de fechar tem 16px.

**D2 — Substituir três popovers artesanais** por `DropdownMenu` do Radix (`ui/dropdown-menu.tsx` já existe e nunca foi usado): `transactions-list.tsx:361`, `actor-sub-transactions-table.tsx:61`, `loans-page.tsx:62`. Os três são o mesmo padrão copiado — `getBoundingClientRect()`, depois `{ top: rect.bottom + 4, left: rect.right - largura }` num portal com `position: fixed`, sem clamp em nenhum eixo. O de `transactions-list` tem estouro vertical confirmado (menu de ~112px numa linha cujo topo fica abaixo de ~540px).

**D3 — Diálogos.**

- `ui/dialog.tsx:60` — `max-h-[85vh]` → `max-h-[85dvh]`. O iOS não encolhe o viewport de layout quando o teclado abre.
- Remover `autoFocus` de `add-actor-dialog.tsx:80` e `edit-actor-dialog.tsx:89` — abrem o teclado sozinhos ao montar.
- `share-actor-dialog.tsx:104-110` — o mesmo input concentra três problemas: é `readOnly` mas focável e chama `.select()` no clique, abrindo o teclado sobre um campo onde não se digita; sua classe `text-sm` (linha 108) sobrescreve o `text-base` que evita o zoom do iOS; e o diálogo não tem `DialogFooter`, então a única saída é o X de 16px do item acima. É o fluxo mais usado no celular.

**D4 — `overscroll-behavior-x: contain`** nos containers de scroll de tabela (`ui/table.tsx`). Como as tabelas continuam rolando (decisão 5), rolar até o fim à esquerda encadeia no gesto de voltar do Safari e o usuário perde a tela.

**D5 — Duas linhas de alto retorno** (já incluídas no head da seção A): `lang="pt-BR"` e `format-detection: telephone=no`. Sem a segunda, o iOS transforma valores, datas e números de documento em links azuis de telefone — frequente num app de contas.

## Fora de escopo

Declarado explicitamente para não parecer esquecimento:

- **Cache de dados offline e fila de escrita** — decisão 2.
- **Push notifications** — não pedido; fraco no iOS.
- **Fotografar comprovante PIX.** É o caso de uso mais óbvio de celular e **não funciona** — mas o bloqueio é no backend, não no `accept=` do frontend. `upload_pix_receipt.py:47` roda `extract_text_from_pdf` e rejeita explicitamente PDF que é imagem ("parece ser uma imagem. Use entrada manual"). Não existe caminho de OCR nem de modelo de visão. Habilitar imagem exige trabalho de backend.
- **Reescrever tabelas como cards** — decisão 5.
- **Extrair o seletor de mês duplicado** em `dashboard-page.tsx`, `actors-page.tsx` e `public-actor-page.tsx` — refactor não relacionado.
- **Chamada dupla de `GET /user/me/`** (`auth-context.tsx:33` e `user-context.tsx:21`) — dois spinners em série no cold start, ruim em 4G. Vale a pena, mas é mudança de contexto de auth, não de PWA.
- **Bugs reais achados de passagem:** título fixo `Receitas` na aba Despesas (`transactions-list.tsx:238`); expandir linha refaz o request (falta `forceMount`); `COPY frontend/ .` depois do `yarn install` no `Dockerfile.frontend` sobrescreve o `node_modules` do container pelo do host (não há `.dockerignore`); `docker-compose.prod.yml` e `nginx/poupix-frontend.conf` disputam a porta 80; `services/auth/refresh.ts:14` cai para `http://localhost:8000` enquanto os outros três caem para produção.

## Verificação

Nada aqui tem lógica de negócio, então o repositório não ganha suite nova. A verificação é de comportamento observável:

1. **Build passa:** `yarn build` gera `dist/sw.js` e `dist/manifest.webmanifest`.
2. **Instalabilidade:** Lighthouse categoria PWA em `https://poupix.connectakit.com.br` — critério "installable" verde. É a checagem que cobre manifest, ícones, service worker com fetch handler e HTTPS de uma vez.
3. **Casca offline:** com o app instalado, modo avião, abrir — a UI monta e os dados mostram erro de rede em vez de tela em branco.
4. **Esconder AI:** no app instalado o menu tem três abas; no navegador, no mesmo celular, as seis entradas continuam lá e `/chat` abre.
5. **Cache do service worker:** `curl -sI https://poupix.connectakit.com.br/sw.js | grep -i cache-control` não deve conter `immutable`.
6. **Safe area:** em iPhone com notch, instalado, a barra de abas fica acima do indicador de home.
7. **Gesto de voltar:** rolar a tabela de transações totalmente à esquerda e continuar — não deve navegar para trás.

Os itens 2, 3, 4, 6 e 7 exigem um celular real. Não dá para fingir isso em CI.

## Riscos

1. **A qual nginx a correção de cache se aplica** — não determinável pelo repositório. Mitigado corrigindo os dois. Se houver um terceiro caminho de deploy não versionado, o `sw.js` imutável reaparece e é irreversível para quem já instalou.
2. **Barra de abas no desktop** — o usuário escolheu sem restringir a celular. Pode não agradar quando vir; a volta é uma condição de breakpoint.
3. **`display-mode: standalone` no iOS antigo** — Safari mais velho reporta por `navigator.standalone`, não por media query. Ambos verificados no hook. Se falhar, o resultado é o menu completo aparecer no app instalado: degrada visível, não quebra.
4. **`autoUpdate` do vite-plugin-pwa** troca o service worker sem perguntar. Combinado com um formulário aberto, pode recarregar durante o preenchimento. Aceito para um app de usuário único.
5. **Precache amplia o custo de qualquer arquivo indevido em `dist/`.** O `vite-plugin-pwa` seleciona por glob sobre a saída do build, então tudo que estiver ali no momento do build passa a ser copiado para o cache do navegador de cada visitante — não só servido sob demanda. Hoje já existe um `frontend/dist/foo.secret` com uma credencial de servidor (não rastreado no git; `dist/` está no `.gitignore`). Duas providências: tirar o arquivo de `dist/` antes de qualquer build, e restringir `workbox.globPatterns` às extensões esperadas (`js,css,html,svg,png,webmanifest`) em vez de aceitar o diretório inteiro. A segunda é a que continua valendo depois que alguém esquecer a primeira.
