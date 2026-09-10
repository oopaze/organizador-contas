# Poupix como app instalável (PWA) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tornar o frontend web existente instalável na tela inicial do celular, escondendo as telas de AI/MCP no app instalado e corrigindo o que atrapalha o uso com o polegar — sem reescrever a UI.

**Architecture:** Trabalho aditivo sobre o app React+Vite atual. Um plugin de build gera o service worker e o manifest; um hook detecta o modo instalado e filtra a navegação; uma barra de abas nova entra abaixo do conteúdo. As correções de celular são pontuais em arquivos existentes, com uma substituição de código artesanal por primitiva já instalada.

**Tech Stack:** React 18, TypeScript, Vite 6.3.5, Tailwind v4, Radix UI, `vite-plugin-pwa` (novo), Vitest (novo, dev-only), yarn.

**Spec:** `docs/superpowers/specs/2026-09-09-poupix-pwa-design.md`

## Global Constraints

- **Gerenciador de pacotes: `yarn`.** O `Dockerfile.frontend:11` roda `yarn install --frozen-lockfile`. Existe um `package-lock.json` órfão no repositório — ignore-o, não o atualize.
- **Todo texto visível ao usuário em português (pt-BR).** O app inteiro é em português. Rótulos de aba, `aria-label` e mensagens seguem a mesma língua.
- **Cor da marca: esmeralda.** `theme_color` e o gradiente dos ícones usam `#059669` (emerald-600) → `#10b981` (emerald-500). O índigo atual do favicon é o elemento fora do tom e será substituído.
- **Alvo de toque mínimo: 44×44px** para qualquer ação destrutiva ou primária. Em Tailwind: `size-11`. O `size="icon"` padrão do projeto é `size-9` (36px) e continua aceitável para ações não destrutivas.
- **Nada de dependência nova em runtime.** `vite-plugin-pwa` e `vitest` são `devDependencies`. O `DropdownMenu` da Task 8 usa `@radix-ui/react-dropdown-menu`, que **já está** no `package.json`.
- **Viewport alvo dos checks manuais: 390×844** (iPhone 14).
- **Não tocar nas tabelas.** Decisão 5 do spec: elas já rolam horizontalmente e ficam como estão. Nenhuma tarefa aqui converte tabela em cards nem esconde colunas.
- **`frontend/dist/` é a raiz web publicada.** Nada de segredo, nota ou arquivo temporário ali. O `.gitignore` da raiz já cobre `*.secret`.

---

## Estrutura de arquivos

**Criados:**

| Arquivo | Responsabilidade |
|---|---|
| `frontend/public/icon-maskable.svg` | Fonte SVG quadrada full-bleed para os ícones opacos (maskable e apple-touch) |
| `frontend/public/icon-192.png` | Ícone do manifest, `purpose: any` |
| `frontend/public/icon-512.png` | Ícone do manifest, `purpose: any` |
| `frontend/public/icon-maskable-512.png` | Ícone do manifest, `purpose: maskable` |
| `frontend/public/apple-touch-icon.png` | Tile da tela inicial do iOS, 180×180, opaco |
| `frontend/src/vite-env.d.ts` | Tipos do Vite e do `virtual:pwa-register` |
| `frontend/src/app/components/nav-items.ts` | Fonte única dos destinos de navegação + a função pura que decide quais aparecem |
| `frontend/src/app/components/nav-items.test.ts` | O único teste automatizado do plano |
| `frontend/src/lib/use-standalone.ts` | Hook que detecta o app instalado |
| `frontend/src/app/components/bottom-tabs.tsx` | Barra de abas inferior |
| `frontend/vitest.config.ts` | Config do runner de teste |

**Modificados:** `frontend/index.html`, `frontend/vite.config.ts`, `frontend/src/main.tsx`, `frontend/package.json`, `frontend/src/app/components/layout.tsx`, `frontend/src/app/components/ui/dialog.tsx`, `frontend/src/app/components/ui/table.tsx`, `frontend/src/app/components/loan-payments-table.tsx`, `frontend/src/app/components/share-actor-dialog.tsx`, `frontend/src/app/components/add-actor-dialog.tsx`, `frontend/src/app/components/edit-actor-dialog.tsx`, `frontend/src/app/components/actor-sub-transactions-table.tsx`, `frontend/src/app/components/transactions-list.tsx`, `frontend/src/app/pages/loans-page.tsx`, `frontend/src/app/pages/actors-page.tsx`, `nginx/poupix-frontend.conf`, `Dockerfile.frontend`.

## Sobre testes neste plano

**O frontend não tem runner de teste nenhum hoje** — sem vitest, sem jest, sem testing-library, sem script `test` no `package.json`. Verificado.

Este plano **não** monta uma suíte para o app inteiro; seria escopo que ninguém pediu. Ele adiciona `vitest` e **um** arquivo de teste, cobrindo a única lógica com ramificação que o plano introduz: quais itens de navegação aparecem no app instalado (Task 5). Essa lógica é extraída como função pura sem DOM, então o teste roda em ambiente node — sem jsdom, sem happy-dom.

Todo o resto são mudanças declarativas (classes CSS, atributos, config de build) cuja verificação honesta é o build passar e o comportamento no aparelho. Cada tarefa diz exatamente o que rodar e o que esperar. As tarefas marcadas **[requer celular]** não podem ser verificadas em CI e precisam de um aparelho real — não finja que passaram.

---

### Task 1: Ícones em esmeralda

Gera os quatro PNGs que o manifest e o iOS consomem, a partir de SVG. Não há ferramenta nova: o `qlmanage` é built-in do macOS e foi verificado renderizando o `favicon.svg` atual em PNG 512×512 limpo.

Dois SVGs de origem, de propósito:
- o **redondo** (`favicon.svg`, já existe) vira os ícones `purpose: any`, que aparecem sobre fundos variados e ficam melhor recortados;
- um **quadrado full-bleed** (novo) vira o maskable e o apple-touch. O maskable precisa preencher o quadrado porque a máscara squircle do Android deixaria os cantos transparentes de um círculo. O apple-touch precisa ser opaco porque o iOS renderiza alpha como preto. O mesmo arquivo resolve os dois, e evita ter que achatar transparência com ferramenta.

**Files:**
- Modify: `frontend/public/favicon.svg` (só as duas paradas do gradiente)
- Create: `frontend/public/icon-maskable.svg`
- Create: `frontend/public/icon-192.png`, `icon-512.png`, `icon-maskable-512.png`, `apple-touch-icon.png`

**Interfaces:**
- Consumes: nada (primeira tarefa)
- Produces: os quatro caminhos PNG acima, referenciados literalmente pelo manifest da Task 3 e pelo `<head>` da Task 2.

- [ ] **Step 1: Recolorir o favicon para esmeralda**

Em `frontend/public/favicon.svg`, trocar as duas paradas do gradiente. Antes:

```xml
    <stop offset="0%" style="stop-color:#4f46e5"/>
    <stop offset="100%" style="stop-color:#6366f1"/>
```

Depois:

```xml
    <stop offset="0%" style="stop-color:#059669"/>
    <stop offset="100%" style="stop-color:#10b981"/>
```

Trocar também o `fill` do miolo do círculo pequeno, que repetia o índigo. Antes: `<circle cx="62" cy="52" r="6" fill="#4f46e5"/>` — depois: `<circle cx="62" cy="52" r="6" fill="#059669"/>`.

- [ ] **Step 2: Criar o SVG quadrado full-bleed**

Criar `frontend/public/icon-maskable.svg`. O grupo interno da carteira é o mesmo do favicon e já cabe na zona segura de 80% (ocupa x 22–78, y 28–70, dentro de 10–90):

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#059669"/>
      <stop offset="100%" style="stop-color:#10b981"/>
    </linearGradient>
  </defs>
  <rect width="100" height="100" fill="url(#bg)"/>
  <g fill="white">
    <rect x="22" y="35" width="56" height="35" rx="4" fill="white" opacity="0.95"/>
    <rect x="22" y="35" width="56" height="12" rx="4" fill="white"/>
    <circle cx="62" cy="52" r="6" fill="#059669"/>
    <circle cx="62" cy="52" r="3" fill="white"/>
    <rect x="40" y="28" width="20" height="4" rx="2" fill="white" opacity="0.8"/>
  </g>
</svg>
```

- [ ] **Step 3: Gerar os quatro PNGs**

```bash
cd frontend/public
qlmanage -t -s 512 -o . favicon.svg          >/dev/null 2>&1
qlmanage -t -s 512 -o . icon-maskable.svg    >/dev/null 2>&1
mv favicon.svg.png icon-512.png
mv icon-maskable.svg.png icon-maskable-512.png
sips -z 192 192 icon-512.png          --out icon-192.png        >/dev/null
sips -z 180 180 icon-maskable-512.png --out apple-touch-icon.png >/dev/null
```

O apple-touch sai do maskable justamente porque aquele é opaco.

- [ ] **Step 4: Conferir dimensões e opacidade**

```bash
cd frontend/public && sips -g pixelWidth -g pixelHeight -g hasAlpha \
  icon-192.png icon-512.png icon-maskable-512.png apple-touch-icon.png
```

Esperado: 192×192, 512×512, 512×512 e 180×180 respectivamente. Abrir `apple-touch-icon.png` e confirmar visualmente que não há canto transparente — o quadrado é esmeralda de ponta a ponta.

- [ ] **Step 5: Commit**

```bash
git add frontend/public/favicon.svg frontend/public/icon-maskable.svg \
        frontend/public/icon-192.png frontend/public/icon-512.png \
        frontend/public/icon-maskable-512.png frontend/public/apple-touch-icon.png
git commit -m "feat(pwa): ícones em esmeralda nos tamanhos que o manifest e o iOS pedem"
```

---

### Task 2: Metadados do `<head>`

Cinco linhas no `index.html`. Duas delas (`lang` e `format-detection`) são os itens D5 do spec e valem por si: hoje o app é inteiramente em português declarado como inglês, e o iOS transforma valores e datas em links azuis de telefone.

O `<link rel="manifest">` **não** entra aqui — o manifest é gerado pelo plugin na Task 3, e apontar para um arquivo que ainda não existe deixaria o repositório num estado quebrado entre commits.

**Files:**
- Modify: `frontend/index.html:2-8`

**Interfaces:**
- Consumes: `apple-touch-icon.png` da Task 1
- Produces: `<head>` pronto para o plugin da Task 3 injetar o `<link rel="manifest">`

- [ ] **Step 1: Substituir o `<head>`**

O arquivo atual tem indentação de dois espaços na raiz; preserve. Antes:

```html
  <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
      <title>Poupix</title>
    </head>
```

Depois:

```html
  <html lang="pt-BR">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
      <meta name="format-detection" content="telephone=no" />
      <meta name="theme-color" content="#059669" />
      <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
      <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
      <title>Poupix</title>
    </head>
```

- [ ] **Step 2: Build passa**

Run: `cd frontend && yarn build`
Expected: build conclui sem erro; `dist/index.html` contém `lang="pt-BR"` e `viewport-fit=cover`.

```bash
grep -o 'lang="pt-BR"' frontend/dist/index.html
grep -o 'viewport-fit=cover' frontend/dist/index.html
```

Ambos devem imprimir uma linha.

- [ ] **Step 3: Commit**

```bash
git add frontend/index.html
git commit -m "feat(pwa): head com lang pt-BR, theme-color e apple-touch-icon

format-detection=telephone=no evita o iOS transformar valores e datas
em links de telefone. viewport-fit=cover é pré-requisito da safe-area
que a barra de abas vai usar."
```

---

### Task 3: Service worker e manifest

O `vite-plugin-pwa` gera as duas coisas. O manifest fica declarado no `vite.config.ts` em vez de um `public/manifest.webmanifest` escrito à mão — assim há uma fonte só, e o plugin injeta o `<link rel="manifest">` sozinho.

`globPatterns` é restrito por extensão de propósito (risco 5 do spec): o precache copia tudo que casar para o navegador de cada visitante, então aceitar `dist/**` inteiro transformaria qualquer arquivo esquecido ali em algo distribuído.

**Files:**
- Modify: `frontend/package.json` (devDependency)
- Modify: `frontend/vite.config.ts`
- Create: `frontend/src/vite-env.d.ts`
- Modify: `frontend/src/main.tsx`

**Interfaces:**
- Consumes: os PNGs da Task 1; o `<head>` da Task 2
- Produces: `dist/sw.js` e `dist/manifest.webmanifest` no build — os dois arquivos cujo cache a Task 4 precisa desarmar

- [ ] **Step 1: Instalar o plugin**

```bash
cd frontend && yarn add -D vite-plugin-pwa
```

O projeto usa Vite 6.3.5, que precisa de `vite-plugin-pwa` >= 0.21. Se o yarn resolver para algo mais antigo por causa do `pnpm.overrides` no `package.json`, fixe explicitamente: `yarn add -D vite-plugin-pwa@^0.21.0`.

- [ ] **Step 2: Declarar plugin e manifest**

Em `frontend/vite.config.ts`, adicionar o import e a entrada em `plugins`. O comentário existente sobre os plugins do Make deve continuar onde está:

```ts
import { defineConfig } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    // The React and Tailwind plugins are both required for Make, even if
    // Tailwind is not being actively used – do not remove them
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        name: 'Poupix',
        short_name: 'Poupix',
        description: 'Controle suas despesas e receitas',
        lang: 'pt-BR',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#059669',
        icons: [
          { src: '/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: '/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
          { src: '/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        // Restrito por extensão de propósito: o precache distribui para o
        // navegador de cada visitante, então dist/** inteiro é largo demais.
        globPatterns: ['**/*.{js,css,html,svg,png,webmanifest}'],
      },
    }),
  ],
  resolve: {
    alias: {
      // Alias @ to the src directory
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

- [ ] **Step 3: Declarar os tipos do módulo virtual**

Criar `frontend/src/vite-env.d.ts`. Sem isso o TypeScript não conhece `virtual:pwa-register`:

```ts
/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/client" />
```

- [ ] **Step 4: Registrar o service worker**

Em `frontend/src/main.tsx`. O arquivo atual tem indentação de dois espaços; preserve. Antes:

```tsx
  import { createRoot } from "react-dom/client";
  import App from "./app/App.tsx";
  import "./styles/index.css";

  createRoot(document.getElementById("root")!).render(<App />);
```

Depois:

```tsx
  import { createRoot } from "react-dom/client";
  import { registerSW } from "virtual:pwa-register";
  import App from "./app/App.tsx";
  import "./styles/index.css";

  registerSW({ immediate: true });

  createRoot(document.getElementById("root")!).render(<App />);
```

- [ ] **Step 5: Build gera os dois arquivos**

Run: `cd frontend && yarn build`
Expected: build passa e os dois arquivos existem.

```bash
ls -la frontend/dist/sw.js frontend/dist/manifest.webmanifest
```

- [ ] **Step 6: O manifest está válido e completo**

```bash
cd frontend/dist && python3 -c "
import json
m = json.load(open('manifest.webmanifest'))
assert m['display'] == 'standalone', m['display']
assert m['start_url'] == '/', m['start_url']
assert m['theme_color'] == '#059669', m['theme_color']
sizes = {i['sizes'] for i in m['icons']}
assert '192x192' in sizes and '512x512' in sizes, sizes
assert any(i.get('purpose') == 'maskable' for i in m['icons']), 'falta ícone maskable'
print('manifest ok:', m['name'], sorted(sizes))
"
```

Expected: imprime `manifest ok: Poupix ['192x192', '512x512']`.

- [ ] **Step 7: O precache não pegou nada além do esperado**

```bash
grep -o '"url":"[^"]*"' frontend/dist/sw.js | sort -u
```

Expected: só `.js`, `.css`, `.html`, `.svg`, `.png` e o `.webmanifest`. Se aparecer qualquer outra extensão, o `globPatterns` está largo demais — corrija antes de seguir.

- [ ] **Step 8: Commit**

```bash
git add frontend/package.json frontend/yarn.lock frontend/vite.config.ts \
        frontend/src/vite-env.d.ts frontend/src/main.tsx
git commit -m "feat(pwa): service worker e manifest via vite-plugin-pwa

globPatterns é restrito por extensão: o precache é distribuído para o
navegador de cada visitante, então dist/** inteiro seria largo demais."
```

---

### Task 4: Desarmar o cache do service worker no nginx

**A tarefa mais consequente do plano, e a única irreversível se sair errada.** O nginx embutido no `Dockerfile.frontend` cacheia por extensão com `expires 1y; immutable`, e o regex inclui `js`. O service worker se chama `sw.js`. Publicado assim, ele fica congelado por um ano no navegador de quem instalar, e nenhuma correção posterior chega — do lado do servidor não há como puxar de volta.

Existem **duas** configs nginx divergentes no repositório e não é possível determinar pelo repositório qual está no ar: `deploy-hostinger.sh` sobe `docker-compose.prod.yml` (que constrói o `Dockerfile.frontend`), mas `nginx/poupix-frontend.conf` serve `/var/www/poupix` direto com TLS. **A correção vai nas duas.** Custa quatro linhas e dispensa a investigação.

Em nginx, `location =` (match exato) tem precedência sobre `location ~*` (regex), independente da ordem no arquivo. Ainda assim, colocar os blocos exatos antes do regex deixa a intenção legível.

**Files:**
- Modify: `Dockerfile.frontend:29-33` (dentro do heredoc)
- Modify: `nginx/poupix-frontend.conf:11-14`

**Interfaces:**
- Consumes: `dist/sw.js` e `dist/manifest.webmanifest` da Task 3
- Produces: nada consumido por tarefas seguintes

- [ ] **Step 1: Corrigir o nginx do Dockerfile**

Em `Dockerfile.frontend`, dentro do heredoc, inserir os dois blocos **antes** do `location ~*` existente. Note que dentro do heredoc as variáveis levam escape (`\$uri`) — os blocos novos não usam variável nenhuma, então não há o que escapar. Antes:

```
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
```

Depois:

```
    # O service worker e o shell NUNCA podem ser imutáveis: sw.js casa com
    # o regex de assets abaixo, e um sw.js congelado por um ano trava o app
    # instalado numa versão para sempre.
    location = /sw.js {
        add_header Cache-Control "no-cache";
    }

    location = /index.html {
        add_header Cache-Control "no-cache";
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
```

- [ ] **Step 2: Corrigir o nginx do host**

Em `nginx/poupix-frontend.conf`, inserir os mesmos dois blocos antes do `location /assets/`. Esta config só cacheia `/assets/` (onde o Vite põe os arquivos com hash), então o `sw.js` na raiz já escapava — mas o `index.html` não tinha diretiva nenhuma e ficava a cargo do heurístico do navegador. Antes:

```
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
```

Depois:

```
    location = /sw.js {
        add_header Cache-Control "no-cache";
    }

    location = /index.html {
        add_header Cache-Control "no-cache";
    }

    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
```

- [ ] **Step 3: Validar a sintaxe das duas configs**

```bash
cd /Users/josepedrodasilvagomes/Projects/personal/bills-manager
docker run --rm -v "$PWD/nginx/poupix-frontend.conf:/etc/nginx/conf.d/test.conf:ro" \
  nginx:alpine nginx -t
```

Expected: `syntax is ok` e `test is successful`. O bloco TLS referencia certificados que não existem no container, então se o erro for sobre `ssl_certificate`, a sintaxe passou — o que importa é não haver erro de parsing nos blocos novos.

Para o heredoc do Dockerfile, a validação é o próprio build:

```bash
docker build -f Dockerfile.frontend -t poupix-fe-test . && \
docker run --rm poupix-fe-test nginx -t
```

Expected: `syntax is ok`.

- [ ] **Step 4: Confirmar o efeito no container**

```bash
docker run -d --rm -p 8099:80 --name poupix-fe-test poupix-fe-test
curl -sI http://localhost:8099/sw.js | grep -i '^cache-control'
curl -sI http://localhost:8099/assets/ 2>/dev/null | head -1
docker stop poupix-fe-test
```

Expected: a linha do `sw.js` traz `Cache-Control: no-cache` e **não** contém `immutable`.

- [ ] **Step 5: Commit**

```bash
git add Dockerfile.frontend nginx/poupix-frontend.conf
git commit -m "fix(nginx): impedir cache imutável de sw.js e index.html

O regex de assets do Dockerfile casa com sw.js e o marcava como
immutable por um ano — o que trava o app instalado numa versão sem
volta. Aplicado nas duas configs porque não dá para determinar pelo
repositório qual está em produção."
```

---

### Task 5: Esconder AI/MCP no app instalado

Detecta o modo instalado e filtra a navegação. A lista de destinos sai de dentro do JSX do `layout.tsx` e vira dado em arquivo próprio, porque a Task 6 precisa da mesma lista para montar as abas — sem isso as duas navegações divergiriam na primeira mudança.

A decisão de quais itens aparecem é uma função pura de um booleano. É a única lógica com ramificação do plano, e é o que o teste cobre.

O acoplamento das telas de AI é zero: verificado por grep na árvore inteira, nada fora daquelas quatro páginas importa `services/chat`, `services/ai` ou `services/mcp`. Nenhuma rota é removida — `routes.tsx` não é tocado, e as telas continuam abrindo pelo navegador.

`/oauth/authorize` não entra na lista: nunca esteve no menu, é alvo de redirect vindo do Claude Desktop / ChatGPT.

**Files:**
- Create: `frontend/src/lib/use-standalone.ts`
- Create: `frontend/src/app/components/nav-items.ts`
- Create: `frontend/src/app/components/nav-items.test.ts`
- Create: `frontend/vitest.config.ts`
- Modify: `frontend/package.json` (devDependency + script `test`)
- Modify: `frontend/src/app/components/layout.tsx:5,28-92`

**Interfaces:**
- Consumes: nada de tarefas anteriores
- Produces:
  - `NAV_ITEMS: NavItem[]` e `visibleNavItems(standalone: boolean): NavItem[]` de `@/app/components/nav-items`, onde `NavItem = { to: string; label: string; icon: LucideIcon; hideWhenInstalled?: boolean }`
  - `useStandalone(): boolean` de `@/lib/use-standalone`

  A Task 6 consome os dois.

- [ ] **Step 1: Instalar o vitest e adicionar o script**

```bash
cd frontend && yarn add -D vitest
```

Em `frontend/package.json`, adicionar a entrada em `scripts`, ao lado das existentes:

```json
  "scripts": {
    "build": "vite build",
    "dev": "vite",
    "test": "vitest run"
  },
```

- [ ] **Step 2: Config do vitest**

Criar `frontend/vitest.config.ts`. Ambiente node de propósito — a função sob teste é pura e não toca DOM, então não há jsdom para instalar:

```ts
import { defineConfig } from 'vitest/config'
import path from 'path'

export default defineConfig({
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

- [ ] **Step 3: Escrever o teste que falha**

Criar `frontend/src/app/components/nav-items.test.ts`:

```ts
import { describe, it, expect } from 'vitest';
import { NAV_ITEMS, visibleNavItems } from './nav-items';

describe('visibleNavItems', () => {
  it('mostra todos os destinos no navegador', () => {
    expect(visibleNavItems(false)).toHaveLength(NAV_ITEMS.length);
  });

  it('esconde chat, ai-insights e integrations no app instalado', () => {
    const rotas = visibleNavItems(true).map((i) => i.to);
    expect(rotas).toEqual(['/', '/loans', '/actors']);
  });

  it('nunca esconde as telas de dinheiro', () => {
    const rotas = visibleNavItems(true).map((i) => i.to);
    for (const r of ['/', '/loans', '/actors']) {
      expect(rotas).toContain(r);
    }
  });

  it('não perde nenhum destino que existia no menu do web', () => {
    const rotas = NAV_ITEMS.map((i) => i.to);
    expect(rotas).toEqual([
      '/', '/loans', '/actors', '/chat', '/integrations', '/ai-insights',
    ]);
  });
});
```

O último caso é a rede de segurança contra a regressão mais provável desta tarefa: mover a nav para um arquivo novo e derrubar um item sem perceber.

- [ ] **Step 4: Rodar e ver falhar**

Run: `cd frontend && yarn test`
Expected: FAIL — `Failed to resolve import "./nav-items"`.

- [ ] **Step 5: Implementar**

Criar `frontend/src/app/components/nav-items.ts`. A ordem e os rótulos vêm dos `title=` que já existem no `layout.tsx`:

```ts
import { Home, Users, MessageSquare, Brain, Plug, HandCoins } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  /** Telas de AI/MCP: somem do app instalado, seguem acessíveis pelo navegador. */
  hideWhenInstalled?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Início', icon: Home },
  { to: '/loans', label: 'Empréstimos', icon: HandCoins },
  { to: '/actors', label: 'Atores', icon: Users },
  { to: '/chat', label: 'Assistente IA', icon: MessageSquare, hideWhenInstalled: true },
  { to: '/integrations', label: 'Integrações', icon: Plug, hideWhenInstalled: true },
  { to: '/ai-insights', label: 'AI Insights', icon: Brain, hideWhenInstalled: true },
];

export function visibleNavItems(standalone: boolean): NavItem[] {
  return standalone ? NAV_ITEMS.filter((i) => !i.hideWhenInstalled) : NAV_ITEMS;
}
```

- [ ] **Step 6: Rodar e ver passar**

Run: `cd frontend && yarn test`
Expected: PASS, 4 testes.

- [ ] **Step 7: O hook de detecção**

Criar `frontend/src/lib/use-standalone.ts`. Duas checagens porque o Safari mais antigo não responde pela media query:

```ts
import { useEffect, useState } from 'react';

const QUERY = '(display-mode: standalone)';

function detect(): boolean {
  if (typeof window === 'undefined') return false;
  // navigator.standalone é o caminho do Safari iOS legado, sem tipo padrão.
  const iosLegacy = (window.navigator as Navigator & { standalone?: boolean }).standalone;
  return window.matchMedia(QUERY).matches || iosLegacy === true;
}

/** true quando rodando como app instalado, não numa aba do navegador. */
export function useStandalone(): boolean {
  const [standalone, setStandalone] = useState(detect);

  useEffect(() => {
    const mql = window.matchMedia(QUERY);
    const onChange = () => setStandalone(detect());
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, []);

  return standalone;
}
```

- [ ] **Step 8: Ligar no layout**

Em `frontend/src/app/components/layout.tsx`, trocar o import de ícones e o bloco `<nav>` inteiro. Antes (linha 5):

```tsx
import { LogOut, Wallet, Home, Users, MessageSquare, Brain, Plug, HandCoins } from 'lucide-react';
```

Depois:

```tsx
import { LogOut, Wallet } from 'lucide-react';
import { visibleNavItems } from '@/app/components/nav-items';
import { useStandalone } from '@/lib/use-standalone';
```

Dentro do componente, logo após `const { user, logout } = useAuth();`:

```tsx
  const standalone = useStandalone();
  const navItems = visibleNavItems(standalone);
```

E substituir todo o bloco `<nav>` (as seis `NavLink` escritas à mão, linhas 28–92) por:

```tsx
            <nav className="flex items-center gap-1 sm:order-2 sm:w-auto justify-center sm:justify-self-center">
              {navItems.map(({ to, label, icon: Icon }) => (
                <NavLink key={to} to={to}>
                  {({ isActive }) => (
                    <Button
                      variant={isActive ? 'secondary' : 'ghost'}
                      size="icon"
                      title={label}
                      aria-label={label}
                    >
                      <Icon className="w-5 h-5" />
                    </Button>
                  )}
                </NavLink>
              ))}
            </nav>
```

O `aria-label` é adição deliberada: `title` vira tooltip no hover, que não existe em toque, então hoje esses botões não têm nome acessível nenhum no celular.

- [ ] **Step 9: Build e teste passam**

Run: `cd frontend && yarn test && yarn build`
Expected: 4 testes passam e o build conclui. O `noUnusedLocals` do `tsconfig.app.json` é estrito — se algum ícone do import antigo ficou para trás, o build acusa.

- [ ] **Step 10: Conferir no navegador**

Run: `cd frontend && yarn dev`, abrir em `http://localhost:5173`, logar.
Expected: os seis ícones continuam no header, como hoje. Nada mudou visualmente no navegador — a filtragem só age no app instalado, que a Task 9 verifica.

- [ ] **Step 11: Commit**

```bash
git add frontend/package.json frontend/yarn.lock frontend/vitest.config.ts \
        frontend/src/lib/use-standalone.ts \
        frontend/src/app/components/nav-items.ts \
        frontend/src/app/components/nav-items.test.ts \
        frontend/src/app/components/layout.tsx
git commit -m "feat(pwa): esconder telas de AI/MCP no app instalado

A navegação vira dado num arquivo só, para o header e a barra de abas
não divergirem. Rotas não mudam: as telas seguem acessíveis pelo
navegador. Ganha aria-label de quebra — title não existe em toque."
```

---

### Task 6: Barra de abas inferior

Três destinos na altura do polegar, com rótulo em texto. Consome a mesma lista da Task 5, então nunca diverge do header.

`viewport-fit=cover` (Task 2) é o que faz `env(safe-area-inset-bottom)` resolver para algo diferente de zero. Sem a barra, o modo `contain` padrão do iOS já mantinha o conteúdo fora do notch — a safe-area vira necessária **por causa** desta tarefa, não apesar dela.

O usuário escolheu a barra sem restringir a celular, então ela aparece no desktop também. É deliberado.

**Files:**
- Create: `frontend/src/app/components/bottom-tabs.tsx`
- Modify: `frontend/src/app/components/layout.tsx`

**Interfaces:**
- Consumes: `visibleNavItems`, `useStandalone` da Task 5
- Produces: `<BottomTabs />`, usado só pelo `layout.tsx`

- [ ] **Step 1: Criar o componente**

Criar `frontend/src/app/components/bottom-tabs.tsx`:

```tsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { visibleNavItems } from '@/app/components/nav-items';
import { useStandalone } from '@/lib/use-standalone';

export const BottomTabs: React.FC = () => {
  const items = visibleNavItems(useStandalone());

  return (
    <nav
      className="fixed bottom-0 inset-x-0 z-40 flex border-t border-gray-200 bg-white
                 pb-[env(safe-area-inset-bottom)]"
      aria-label="Navegação principal"
    >
      {items.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          className="flex flex-1 flex-col items-center justify-center gap-1 py-2 min-h-14"
        >
          {({ isActive }) => (
            <>
              <Icon className={`w-5 h-5 ${isActive ? 'text-emerald-600' : 'text-gray-500'}`} />
              <span className={`text-[11px] leading-none ${isActive ? 'text-emerald-600 font-medium' : 'text-gray-500'}`}>
                {label}
              </span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
};
```

`end={to === '/'}` importa: sem isso o `NavLink` de `/` fica ativo em toda rota, porque toda rota começa com barra.

- [ ] **Step 2: Montar no layout e abrir espaço**

Em `frontend/src/app/components/layout.tsx`, importar:

```tsx
import { BottomTabs } from '@/app/components/bottom-tabs';
```

O `<main>` precisa de espaço embaixo ou o último item da lista fica atrás da barra. Antes:

```tsx
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-w-0 overflow-x-clip">
        <Outlet />
      </main>
```

Depois:

```tsx
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 min-w-0 overflow-x-clip
                       pb-[calc(3.5rem+env(safe-area-inset-bottom)+2rem)]">
        <Outlet />
      </main>

      <BottomTabs />
```

`3.5rem` é o `min-h-14` da barra; `2rem` preserva o respiro do `py-8` que existia.

- [ ] **Step 3: Build passa**

Run: `cd frontend && yarn build`
Expected: build conclui sem erro.

- [ ] **Step 4: Conferir no navegador**

Run: `cd frontend && yarn dev`, abrir, logar, e estreitar a janela para 390px de largura.
Expected: barra fixa embaixo com três ou seis abas (seis no navegador — a filtragem só age no app instalado), cada uma com ícone e rótulo legível. Rolar até o fim de uma lista longa: o último item fica acima da barra, não atrás dela. A aba ativa fica esmeralda e muda ao navegar.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/app/components/bottom-tabs.tsx frontend/src/app/components/layout.tsx
git commit -m "feat(pwa): barra de abas inferior com rótulo em texto

Consome a mesma lista do header. Rótulo em texto porque os ícones só
tinham title, que não aparece em toque. Padding inferior no main para o
último item não ficar atrás da barra."
```

---

### Task 7: Alvos de toque e nomes acessíveis (D1)

Hoje há ações destrutivas de 32px, coladas nas vizinhas, rotuladas só por `title=` — que nunca aparece em toque — e duas sem rótulo nenhum. No `loans-page` a célula "Ações" tem cinco ícones cinzas sem separação, e um deles apaga o empréstimo e todos os pagamentos.

Isto não é polimento. É a única tarefa do plano que previne perda de dado.

O spec lista, no mesmo item D1, os gatilhos `⋮` de `actor-sub-transactions-table.tsx:208` e de `transactions-list.tsx`. Eles **não** são tratados aqui: os dois desaparecem na Task 8, que os reescreve já com `aria-label`. Tocá-los nas duas tarefas geraria conflito.

**Files:**
- Modify: `frontend/src/app/pages/loans-page.tsx:248-278, 235`
- Modify: `frontend/src/app/pages/actors-page.tsx:435-461`
- Modify: `frontend/src/app/components/loan-payments-table.tsx:62`
- Modify: `frontend/src/app/components/ui/dialog.tsx:66`

**Interfaces:**
- Consumes: nada
- Produces: nada

- [ ] **Step 1: Separar e rotular a célula de ações dos empréstimos**

Em `frontend/src/app/pages/loans-page.tsx`, o contêiner não tem `gap` e os cinco controles ficam encostados. Antes:

```tsx
                      <div className="inline-flex items-center justify-end">
```

Depois:

```tsx
                      <div className="inline-flex items-center justify-end gap-1">
```

E o botão de remover — o destrutivo — vai a 44px e ganha nome acessível. Antes:

```tsx
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(l.id)} title="Remover"><Trash2 className="w-4 h-4 text-red-600" /></Button>
```

Depois:

```tsx
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-11"
                          onClick={() => handleDelete(l.id)}
                          title="Remover"
                          aria-label="Remover empréstimo"
                        >
                          <Trash2 className="w-4 h-4 text-red-600" />
                        </Button>
```

Os outros quatro controles da célula (`Adicionar pagamento`, o link `Baixar comprovante`, `Compartilhar`, `Editar`) ganham `aria-label` com o mesmo texto do `title`, mas mantêm `size="sm"` — não são destrutivos e o `gap-1` já os separa do vizinho perigoso.

- [ ] **Step 2: Aumentar o chevron de expandir**

Ainda em `loans-page.tsx`, é o único caminho até os pagamentos de um empréstimo e hoje tem 32px. Antes:

```tsx
                      <Button variant="ghost" size="sm" onClick={() => toggle(l.id)}>
```

Depois:

```tsx
                      <Button
                        variant="ghost"
                        size="icon"
                        className="size-11"
                        onClick={() => toggle(l.id)}
                        aria-label={expanded.has(l.id) ? 'Recolher pagamentos' : 'Ver pagamentos'}
                      >
```

- [ ] **Step 3: Rotular editar e apagar de atores**

Em `frontend/src/app/pages/actors-page.tsx`, os botões de editar e apagar não têm `title` **nem** `aria-label` — no celular são dois ícones cinzas indistinguíveis, e um apaga o ator. O de apagar também vai a 44px. Antes:

```tsx
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-muted-foreground hover:text-primary"
                                onClick={(e) => handleEditClick(actor, e)}
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-muted-foreground hover:text-destructive"
                                onClick={(e) => handleDeleteClick(actor, e)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
```

Depois:

```tsx
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 text-muted-foreground hover:text-primary"
                                onClick={(e) => handleEditClick(actor, e)}
                                title="Editar"
                                aria-label="Editar ator"
                              >
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="size-11 text-muted-foreground hover:text-destructive"
                                onClick={(e) => handleDeleteClick(actor, e)}
                                title="Remover"
                                aria-label="Remover ator"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
```

Adicionar também `aria-label="Compartilhar com este ator"` no botão de compartilhar logo acima, que já tem `title`.

- [ ] **Step 4: Rotular o apagar de pagamento**

Em `frontend/src/app/components/loan-payments-table.tsx`, este botão não tem `title` nem `aria-label` — nome acessível zero. Antes:

```tsx
                <Button variant="ghost" size="sm" onClick={() => handleDelete(p.id)}>
                  <Trash2 className="w-4 h-4" />
                </Button>
```

Depois:

```tsx
                <Button
                  variant="ghost"
                  size="icon"
                  className="size-11"
                  onClick={() => handleDelete(p.id)}
                  title="Remover pagamento"
                  aria-label="Remover pagamento"
                >
                  <Trash2 className="w-4 h-4 text-red-600" />
                </Button>
```

- [ ] **Step 5: Aumentar o X de fechar dos diálogos**

Em `frontend/src/app/components/ui/dialog.tsx:66`, o alvo tem 16px — o tamanho do ícone, sem padding. Um `p-2` leva a área tocável a 32px e o `size-11` do wrapper a 44px, sem mexer no ícone. Trocar `absolute top-4 right-4 rounded-xs` por:

```
absolute top-2 right-2 inline-flex size-11 items-center justify-center rounded-md
```

O restante da string de classes fica igual. O `<span className="sr-only">Close</span>` que já existe vira o nome acessível — trocar o texto para `Fechar`, já que o resto do app é em português.

- [ ] **Step 6: Build e testes passam**

Run: `cd frontend && yarn test && yarn build`
Expected: 4 testes passam, build conclui.

- [ ] **Step 7: Conferir no navegador**

Run: `cd frontend && yarn dev`, ir em Empréstimos e em Atores com a janela a 390px.
Expected: os ícones da célula de ações têm respiro visível entre si; o de remover é nitidamente maior que os vizinhos. Inspecionando qualquer um deles no DevTools, existe `aria-label` com texto em português. Abrir um diálogo: o X de fechar é fácil de acertar.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/app/pages/loans-page.tsx frontend/src/app/pages/actors-page.tsx \
        frontend/src/app/components/loan-payments-table.tsx \
        frontend/src/app/components/ui/dialog.tsx
git commit -m "fix(a11y): alvos de 44px e nomes acessíveis nas ações destrutivas

Cinco ícones colados de 32px na célula de ações dos empréstimos, um
deles apagando o empréstimo e todos os pagamentos. Editar e apagar de
atores não tinham título nem aria-label. title vira tooltip no hover,
que não existe em toque."
```

---

### Task 8: Trocar os três popovers artesanais por Radix (D2)

Os três são o mesmo padrão copiado: `getBoundingClientRect()`, depois `{ top: rect.bottom + 4, left: rect.right - largura }` num portal com `position: fixed`, mais um listener de `mousedown` para fechar. Nenhum tem clamp em nenhum eixo. O de `transactions-list` tem estouro vertical confirmado — o menu tem ~112px e some para fora da tela quando a linha está na metade de baixo.

O `ui/dropdown-menu.tsx` já existe no projeto e nunca foi usado. Ele traz detecção de colisão, flip, foco por teclado e fechamento por clique fora. **Esta tarefa remove mais código do que adiciona.**

**Files:**
- Modify: `frontend/src/app/pages/loans-page.tsx:2,45-70,295-322`
- Modify: `frontend/src/app/components/actor-sub-transactions-table.tsx:2,~30-75,206-260`
- Modify: `frontend/src/app/components/transactions-list.tsx:~340-420`

**Interfaces:**
- Consumes: nada
- Produces: nada

- [ ] **Step 1: Converter o menu dos empréstimos**

Em `frontend/src/app/pages/loans-page.tsx`, apagar: o import de `createPortal` (linha 2), o estado `menuFor`, o `useEffect` que escuta `scroll`/`resize`, a função `openMenu`, e o bloco `{menuFor && createPortal(...)}` inteiro (linhas 295–322).

Adicionar o import:

```tsx
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem,
} from '@/app/components/ui/dropdown-menu';
```

Substituir o botão que chamava `openMenu` por:

```tsx
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm" title="Adicionar pagamento" aria-label="Adicionar pagamento">
                              <Plus className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-56">
                            <DropdownMenuItem onSelect={() => setUploadFor(l.id)}>
                              <Upload className="w-4 h-4 mr-2" /> Subir comprovante PIX
                            </DropdownMenuItem>
                            <DropdownMenuItem onSelect={() => setManualFor(l.id)}>
                              <FilePlus className="w-4 h-4 mr-2" /> Entrada manual
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
```

`align="end"` reproduz o alinhamento à direita que o `rect.right - 224` tentava fazer à mão, e o Radix corrige sozinho quando não cabe.

- [ ] **Step 2: Converter o menu das sub-transações de ator**

Em `frontend/src/app/components/actor-sub-transactions-table.tsx`, apagar: o import de `createPortal`, os estados `openPopoverId` e `popoverPosition`, o `dropdownRef`, o `buttonRefs`, o `useEffect` de `handleClickOutside`, a função `handleTogglePopover`, e o bloco `createPortal` do final (linhas 231–260).

Substituir o botão e o menu por:

```tsx
                  <div className="flex items-center justify-end gap-1">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          title="Mais opções"
                          aria-label="Mais opções"
                          onClick={(e) => e.stopPropagation()}
                          onPointerDown={(e) => e.stopPropagation()}
                        >
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-40">
                        <DropdownMenuItem onSelect={() => handlePayClick(subTransaction)}>
                          <CheckCircle className="w-4 h-4 mr-2" />
                          {subTransaction.paid_at ? 'Despagar' : 'Pagar'}
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
```

Os `stopPropagation` continuam necessários: a linha da tabela é um `CollapsibleTrigger`, e sem eles abrir o menu também expande a linha.

Em `handlePayClick`, apagar as duas linhas que zeravam o popover (`setOpenPopoverId(null)` e `setPopoverPosition(null)`) — o estado não existe mais.

- [ ] **Step 3: Ajustar a assinatura dos três handlers de transação**

Em `frontend/src/app/components/transactions-list.tsx`, os três handlers do menu recebem um evento só para chamar `stopPropagation()`, e fecham o popover por estado que vai deixar de existir. Cada um tem exatamente um chamador — o próprio menu — então a assinatura pode encolher sem quebrar mais nada. O Radix fecha o menu sozinho ao selecionar.

Antes (linhas 151, 177 e 201, mesmo formato nos três):

```tsx
  const handlePayClick = (transaction: Transaction, e: React.MouseEvent) => {
    e.stopPropagation();
    setTransactionToPay(transaction);
    setPayDialogOpen(true);
    setOpenPopoverId(null);
  };
```

Depois:

```tsx
  const handlePayClick = (transaction: Transaction) => {
    setTransactionToPay(transaction);
    setPayDialogOpen(true);
  };
```

Aplicar o mesmo corte em `handleRecalculateClick` (que passa a só fazer `setTransactionToRecalculate` + `setRecalculateDialogOpen(true)`) e em `handleGuessCategoryClick` (`setTransactionToGuessCategory` + `setGuessCategoryDialogOpen(true)`).

- [ ] **Step 4: Converter o menu das transações**

Ainda em `transactions-list.tsx`, apagar: os estados `openPopoverId` e `popoverPosition`, o `buttonRefs`, o `useEffect` de clique fora, o `import { Portal }` se ficar sem uso, e o bloco `<Portal>` inteiro (linhas 404–453).

Substituir o botão que calculava `rect.right - 208` e o menu por:

```tsx
                                    <DropdownMenu>
                                      <DropdownMenuTrigger asChild>
                                        <Button
                                          variant="ghost"
                                          size="sm"
                                          title="Mais opções"
                                          aria-label="Mais opções"
                                          onClick={(e) => e.stopPropagation()}
                                          onPointerDown={(e) => e.stopPropagation()}
                                        >
                                          <MoreVertical className="w-4 h-4" />
                                        </Button>
                                      </DropdownMenuTrigger>
                                      <DropdownMenuContent align="end" className="w-52">
                                        <DropdownMenuItem onSelect={() => handlePayClick(transaction)}>
                                          <CheckCircle className="w-4 h-4 mr-2" />
                                          {transaction.is_paid ? 'Despagar' : 'Pagar'}
                                        </DropdownMenuItem>
                                        <DropdownMenuItem onSelect={() => handleRecalculateClick(transaction)}>
                                          <Calculator className="w-4 h-4 mr-2" />
                                          Recalcular
                                        </DropdownMenuItem>
                                        <DropdownMenuItem onSelect={() => handleGuessCategoryClick(transaction)}>
                                          <Sparkles className="w-4 h-4 mr-2" />
                                          Adivinhar Categorias
                                        </DropdownMenuItem>
                                      </DropdownMenuContent>
                                    </DropdownMenu>
```

O menu passa a viver dentro do `map` da linha, então `transaction` está em escopo direto — somem os três `transactions.find(t => t.id === openPopoverId)` que existiam só porque o portal ficava fora do laço.

Adicionar o import no topo do arquivo:

```tsx
import {
  DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem,
} from '@/app/components/ui/dropdown-menu';
```

- [ ] **Step 5: Nenhum vestígio do padrão antigo**

```bash
cd frontend/src
grep -rn "createPortal\|getBoundingClientRect\|popoverPosition\|openPopoverId" app/ | grep -v "ui/"
```

Expected: nenhuma saída. Se sobrar alguma linha, a conversão ficou pela metade.

- [ ] **Step 6: Build e testes passam**

Run: `cd frontend && yarn test && yarn build`
Expected: 4 testes passam, build conclui. O `noUnusedLocals` acusa qualquer import ou estado que ficou órfão.

- [ ] **Step 7: Conferir no navegador**

Run: `cd frontend && yarn dev`, janela a 390px de largura.
Expected, nos três menus (Empréstimos → botão `+`; Atores → expandir um ator → `⋮`; Dashboard → `⋮` numa transação):
- o menu abre inteiro dentro da tela, inclusive numa linha do rodapé da página — este é o bug que a tarefa conserta, então teste especificamente uma linha lá embaixo;
- clicar fora fecha;
- `Esc` fecha;
- abrir o menu numa linha de tabela **não** expande a linha.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/app/pages/loans-page.tsx \
        frontend/src/app/components/actor-sub-transactions-table.tsx \
        frontend/src/app/components/transactions-list.tsx
git commit -m "refactor(fe): trocar três popovers artesanais pelo DropdownMenu do Radix

Os três eram o mesmo padrão copiado, com posição fixa calculada à mão e
sem clamp de viewport — o de transações somia da tela nas linhas de
baixo. O ui/dropdown-menu.tsx já existia e nunca tinha sido usado."
```

---

### Task 9: Diálogos e rolagem de tabela (D3 + D4)

Duas correções pequenas e sem relação entre si, agrupadas porque são as últimas e cada uma é uma linha.

O `85vh` dos diálogos não encolhe quando o teclado do iOS abre, então o botão de enviar fica embaixo do teclado. `dvh` acompanha o viewport visível.

O `overscroll-behavior-x` é a consequência direta de manter as tabelas rolando (decisão 5 do spec): sem ele, arrastar a tabela até o fim à esquerda encadeia no gesto de voltar do Safari e o usuário perde a tela em que estava.

**Files:**
- Modify: `frontend/src/app/components/ui/dialog.tsx:60`
- Modify: `frontend/src/app/components/ui/table.tsx:11`
- Modify: `frontend/src/app/components/add-actor-dialog.tsx:80`
- Modify: `frontend/src/app/components/edit-actor-dialog.tsx:89`
- Modify: `frontend/src/app/components/share-actor-dialog.tsx:104-110`

**Interfaces:**
- Consumes: nada
- Produces: nada

- [ ] **Step 1: Diálogos acompanham o viewport visível**

Em `frontend/src/app/components/ui/dialog.tsx:60`, na string de classes do `DialogPrimitive.Content`, trocar `max-h-[85vh]` por `max-h-[85dvh]`. Nada mais muda na linha.

- [ ] **Step 2: Tirar o autoFocus**

Em `frontend/src/app/components/add-actor-dialog.tsx:80` e `frontend/src/app/components/edit-actor-dialog.tsx:89`, remover a linha `autoFocus`. No celular ela força o teclado a abrir no instante em que o diálogo monta, sem o usuário ter tocado em nada — e é justamente nesses dois diálogos que o teclado mais atrapalha.

- [ ] **Step 3: Consertar o input do compartilhar**

Em `frontend/src/app/components/share-actor-dialog.tsx`, o mesmo input concentra três problemas: `text-sm` derruba a proteção anti-zoom do iOS, é focável apesar de `readOnly` e abre o teclado sobre um campo onde não se digita. Antes:

```tsx
            <Input
              ref={inputRef}
              value={loading ? 'Gerando link…' : shareUrl}
              readOnly
              className="flex-1 text-sm"
              onClick={() => inputRef.current?.select()}
            />
```

Depois:

```tsx
            <Input
              ref={inputRef}
              value={loading ? 'Gerando link…' : shareUrl}
              readOnly
              inputMode="none"
              aria-label="Link de compartilhamento"
              className="flex-1"
              onClick={() => inputRef.current?.select()}
            />
```

`inputMode="none"` mantém o campo focável e selecionável, mas o teclado não sobe. Tirar `text-sm` devolve os 16px que evitam o zoom do iOS.

- [ ] **Step 4: Conter o gesto de voltar nas tabelas**

Em `frontend/src/app/components/ui/table.tsx:11`, o contêiner de rolagem de **toda** tabela do app. Antes:

```tsx
      className="relative w-full overflow-x-auto"
```

Depois:

```tsx
      className="relative w-full overflow-x-auto overscroll-x-contain"
```

- [ ] **Step 5: Build e testes passam**

Run: `cd frontend && yarn test && yarn build`
Expected: 4 testes passam, build conclui.

- [ ] **Step 6: Conferir no navegador**

Run: `cd frontend && yarn dev`, janela a 390px.
Expected: abrir o diálogo de adicionar ator — o teclado/foco **não** salta para o campo sozinho. Abrir o compartilhar de um ator: tocar no link seleciona o texto e o botão de copiar funciona. Rolar a tabela de transações totalmente para a esquerda e continuar arrastando: a página não navega para trás.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/app/components/ui/dialog.tsx \
        frontend/src/app/components/ui/table.tsx \
        frontend/src/app/components/add-actor-dialog.tsx \
        frontend/src/app/components/edit-actor-dialog.tsx \
        frontend/src/app/components/share-actor-dialog.tsx
git commit -m "fix(mobile): dvh nos diálogos, sem autoFocus, e conter o swipe-back

85vh não encolhe com o teclado do iOS aberto e esconde o botão de
enviar. overscroll-x-contain impede que rolar a tabela até a ponta
dispare o gesto de voltar do Safari."
```

---

### Task 10: Verificação no aparelho **[requer celular]**

Nada aqui é automatizável, e é o único ponto onde o trabalho se prova. **Não marque nenhum item sem ter feito no aparelho.** Se um celular não estiver disponível, pare e diga isso — não presuma que passou.

Precisa de um deploy em HTTPS. Produção é `https://poupix.connectakit.com.br`. O deploy é decisão do dono do projeto, não desta tarefa: peça antes de publicar.

**Files:** nenhum (a menos que um defeito apareça)

**Interfaces:**
- Consumes: tudo, das Tasks 1 a 9
- Produces: nada

- [ ] **Step 1: Lighthouse aprova a instalabilidade**

No Chrome desktop, DevTools → Lighthouse, categoria PWA, contra a URL publicada.
Expected: o critério "Web app manifest and service worker meet the installability requirements" passa. Ele cobre manifest, ícones, service worker com fetch handler e HTTPS de uma vez.

- [ ] **Step 2: O header do sw.js está certo em produção**

```bash
curl -sI https://poupix.connectakit.com.br/sw.js | grep -i '^cache-control'
```

Expected: contém `no-cache` e **não** contém `immutable`. Se este check falhar, **pare** — foi o nginx errado que recebeu a correção da Task 4, e cada instalação feita a partir daqui fica presa nesta versão.

- [ ] **Step 3: Instalar no celular**

Android/Chrome: menu → "Instalar app". iOS/Safari: Compartilhar → "Adicionar à Tela de Início".
Expected: o ícone na tela inicial é a carteira esmeralda, não um screenshot da página nem um quadrado cinza. Abrir: sem barra de endereço.

- [ ] **Step 4: As telas de AI sumiram — e só no app**

No app instalado.
Expected: a barra inferior tem exatamente três abas — Início, Empréstimos, Atores. O header não mostra os ícones de chat, integrações e AI insights.

Depois abrir `https://poupix.connectakit.com.br` no navegador do **mesmo** celular.
Expected: os seis destinos continuam lá e `/chat` abre normalmente. É isto que separa "escondido" de "deletado".

- [ ] **Step 5: A casca abre offline**

Com o app instalado e aberto ao menos uma vez, ligar o modo avião e abrir.
Expected: a UI monta — header, abas, estrutura da página. Os dados falham com mensagem de erro de rede. **Não** pode ser tela em branco nem o dinossauro do navegador.

- [ ] **Step 6: Safe area [iPhone com notch]**

Expected: a barra de abas fica acima do indicador de home, sem sobreposição. O header não encosta na Dynamic Island.

- [ ] **Step 7: Gesto de voltar contido**

Ir ao Dashboard, rolar a tabela de transações totalmente para a esquerda e continuar arrastando.
Expected: a página não navega para trás.

- [ ] **Step 8: Teclado não cobre o botão de enviar**

Abrir "Adicionar transação", tocar num campo de texto.
Expected: com o teclado aberto, o botão de enviar continua alcançável rolando dentro do diálogo. O foco não pula para um campo sozinho ao abrir.

- [ ] **Step 9: Os uploads com AI continuam funcionando**

Subir uma fatura em PDF pelo app instalado.
Expected: o parsing por AI roda e as transações aparecem, como antes. Esconder as telas de AI não podia ter afetado isto — é a checagem que prova.

- [ ] **Step 10: Registrar o resultado**

Se tudo passou, o plano está completo. Se algo falhou, abrir uma tarefa nova descrevendo o defeito com o aparelho, o sistema e o passo — não conserte às pressas dentro desta tarefa.

---

## Fora deste plano

Estava no spec como fora de escopo e continua fora. Listado para não parecer esquecimento:

- Cache de respostas da API e escrita offline.
- Push notifications.
- Fotografar comprovante PIX — o bloqueio é no backend (`upload_pix_receipt.py:47` roda `extract_text_from_pdf` e rejeita PDF que é imagem; não há OCR nem modelo de visão).
- Reescrever tabelas como lista de cards, ou esconder colunas.
- Extrair o seletor de mês duplicado em `dashboard-page.tsx`, `actors-page.tsx` e `public-actor-page.tsx`.
- Chamada dupla de `GET /user/me/` em `auth-context.tsx:33` e `user-context.tsx:21`.
- Título fixo `Receitas` na aba Despesas (`transactions-list.tsx:238`).
- Expandir linha refaz o request (falta `forceMount` no `CollapsibleContent`).
- `COPY frontend/ .` depois do `yarn install` no `Dockerfile.frontend`, sem `.dockerignore`.
- Disputa da porta 80 entre `docker-compose.prod.yml` e `nginx/poupix-frontend.conf`.
- `services/auth/refresh.ts:14` cai para `http://localhost:8000` enquanto os outros três caem para produção.
