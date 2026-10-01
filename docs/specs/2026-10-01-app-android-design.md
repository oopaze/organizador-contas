# App Poupix para Android (React Native/Expo) — Design Spec

**Data:** 2026-10-01
**Status:** Design aprovado em conversa; aguardando revisão do spec

## Objetivo

Ter um app Android nativo do Poupix, instalável por APK direto no aparelho (sem loja nesta fase), com paridade das telas do PWA, leitura offline e escrita online. O web atual permanece no ar e não é alterado — continua servindo os fluxos que exigem navegador (`/share/actor`, `/oauth/authorize`) e o uso no desktop.

## Contexto verificado

Levantado do repositório em 2026-10-01:

- **Frontend atual:** React 18 + Vite + Tailwind 4 + Radix/shadcn, 177 arquivos TS/TSX (~17,1k linhas). Telas autenticadas: dashboard (Início), planning (Planejamento), loans (Empréstimos), actors (Atores), settings (Configurações), integrations (Conectores), chat e ai-insights. Públicas: public-actor e oauth-authorize (fluxos de navegador).
- **Estado do main em 2026-10-01:** Modo On (lançamento rápido, extrato/ledger, conciliação de fatura), Planejamento (intenções e projeção) e Cartões já estão implementados — o app porta este estado, não o PWA de setembro.
- **Camada de serviços:** 74 arquivos, ~2,2k linhas, fetch puro com Bearer token e refresh automático em 403 (`frontend/src/services/client.ts`), uploads multipart. API de produção: `https://api.poupix.connectakit.com.br`.
- **Acoplamentos web localizados:** localStorage (tokens), `window.location` (expiração de sessão e OAuth), clipboard (share de ator), `matchMedia` (standalone/mobile), download via `URL.createObjectURL` (ai-insights), `document.*` (copiar/baixar).
- **Sem WebSocket/SSE:** o chat é request/response.
- **Recharts** aparece apenas em `ai-insights-page.tsx`.
- **PWA:** ícones PNG prontos em `frontend/public/` (192, 512, maskable 512, apple-touch) — reaproveitados no app.
- **Máquina de build:** Node 22 + npm 10; sem JDK, sem Android SDK, sem KVM (sem emulador); 7 GB de RAM; 89 GB livres; sem Docker.
- **Backend:** Django + DRF + JWT (access/refresh). Nenhum endpoint novo é necessário para este escopo (cache é client-side; escrita é online).

## Decisões de design

1. **Expo managed + Expo Router + NativeWind** — menor atrito de tooling, ecossistema cobre SecureStore/DocumentPicker/Share, NativeWind preserva o modelo Tailwind do código atual, e o build local de APK é viável (prebuild + Gradle).
2. **Projeto novo em `mobile/`** dentro do monorepo; `android/` gerado por `expo prebuild` e não versionado (sem código nativo custom nesta fase).
3. **Paridade com o PWA:** todas as telas autenticadas entram. As duas públicas ficam no web (`/share/actor` é link compartilhado; `/oauth/authorize` é redirect do Claude Desktop/ChatGPT).
4. **Navegação:** abas embaixo com **Início, Planejamento, Empréstimos, Atores, Mais**. "Mais" lista Conectores, Configurações, Chat IA e Sair — espelha a barra do PWA instalado (que mostra as quatro primeiras) dando porta explícita ao que fica oculto.
5. **Offline somente leitura** (ADR 0002): react-query com persistência em AsyncStorage; leitura responde do cache, refetch em background, banner "Sem conexão — dados de HH:mm". Escrita exige rede e falha com erro honesto.
6. **Auth:** tokens em `expo-secure-store`; refresh em 403 portado de `client.ts`; sessão expirada limpa tokens e volta ao login pelo router.
7. **Uploads:** `expo-document-picker` (PDF/XLSX) mantendo o mesmo `FormData`; **sem câmera** — o backend rejeita comprovante que é imagem (`upload_pix_receipt` exige texto em PDF).
8. **Traduções de UI:** Table → lista de cards; Dialog → Modal do RN; Select/DropdownMenu → bottom sheet; ícones `lucide-react-native` (mesmo conjunto).
9. **Configuração:** `EXPO_PUBLIC_API_URL` no `.env` (default: produção); `USE_MOCK_API` continua constante de código. Nenhuma feature flag nova.
10. **APK:** build local nesta máquina (instalação de JDK + Android SDK), keystore gerado aqui e guardado **fora do git**; saída em `mobile/builds/`. Fallback: EAS Build na conta do usuário.
11. **Modo On, Planejamento e Cartões entram:** já estão no main; o app porta lançamento rápido, extrato, conciliação, intenções/projeção e cartões junto com o resto — tudo no mesmo projeto.
12. **Identidade:** nome "Poupix", package `com.poupix.app`, ícones reaproveitados do PWA.

## Arquitetura

### Estrutura de pastas

```
mobile/
  app/                     # rotas (expo-router)
    _layout.tsx            # providers: auth, react-query, safe-area
    login.tsx
    (tabs)/
      _layout.tsx          # abas: index, planning, loans, actors, more
      index.tsx            # Início (dashboard)
      planning.tsx         # Planejamento
      loans.tsx
      actors.tsx
      more.tsx
    settings.tsx  chat.tsx  integrations.tsx   # stack, fora das abas
  src/
    components/            # primitivos portados + diálogos
    contexts/  lib/
    services/              # cópia 1:1 de frontend/src/services
  assets/                  # ícones do PWA
  builds/                  # APKs gerados (fora do git)
  app.json  package.json  tsconfig.json  tailwind.config.js  babel.config.js
```

### Fluxo de dados

Tela → hook react-query (queryKey por recurso) → `services/` (mesmas assinaturas do PWA) → `client.ts` → API. **Leitura:** cache persistido responde primeiro, refetch em background; sem rede, dados persistidos + banner. **Escrita:** mutation direta; sem rede → erro com aviso.

### Adaptações no porte

- `services/**` mantém arquivos e nomes. `client.ts` muda: `tokenManager` → SecureStore (assíncrono), remove `window.location` (expõe callback de sessão expirada consumido no `_layout`), mantém refresh em 403 e o tratamento de FormData.
- `contexts/auth-context` e `user-context` portados; `lib/category-colors` portado.
- `use-standalone` e `use-mobile` morrem (não fazem sentido no app nativo).

## Equivalências de componentes

Os 21 primitivos em uso no PWA têm equivalente direto:

| PWA (web) | App (RN) |
|---|---|
| Table | lista de cards (`FlatList`) |
| Dialog / AlertDialog | `Modal` do RN + componente `Dialog` |
| Sheet | `@gorhom/bottom-sheet` |
| DropdownMenu / Select | bottom sheet de opções |
| ScrollArea | `ScrollView` / `FlatList` |
| Popover (seletor de mês) | bottom sheet de calendário/lista |
| Switch | port direto |
| Button, Card, Input, Label, Checkbox, Badge, Skeleton, Collapsible, RadioGroup, Tabs, Textarea | portes diretos com NativeWind |

## Tratamento de erro

- **Sem rede na leitura:** banner persistente com timestamp do último sync; ações de escrita mostram "Sem conexão — tente de novo quando voltar".
- **403:** tenta refresh; falhou → limpa tokens e `router.replace('/login')`.
- **Upload:** erro do backend exibido no diálogo (mesmo comportamento do PWA).

## Verificação

1. `npx tsc --noEmit` e testes (`jest-expo`) passam.
2. APK instala no aparelho do usuário por transferência direta (minSdk da Expo SDK vigente).
3. Login contra produção; dashboard lista transações; modo avião mostra os últimos dados com banner.
4. Uploads (fatura, planilha, PIX, arquivo de empréstimo) funcionam pelo seletor de arquivo.
5. CRUD de atores, empréstimos, pagamentos, cartões e configurações; planejamento (intenções/projeção) e compartilhar link funcionam.
6. Chat e Conectores abrem e executam.
7. Sem rede, escrita mostra erro honesto (não trava, não duplica).

## Fora de escopo

Publicação em loja, push notifications, câmera, escrita offline/fila de sincronização, expo-updates/OTA, alvo web universal, **Insights IA** (decisão do usuário em 2026-10-01 — a tela continua no web), alterações no `frontend/` ou no backend.

## Riscos

1. **Build local do APK com 7 GB de RAM** — mitigação: Gradle sem daemon e limites de memória; fallback EAS Build.
2. **Sem emulador nesta máquina** — verificação visual é no aparelho do usuário. Mitigação: APK cedo (após o dashboard) e typecheck/testes aqui.
3. **Paridade visual não é 1:1** — tabelas viram cards por decisão; a primeira entrega já mostra o padrão para validar.
4. **Cada mudança = novo APK** (sem OTA) — aceito nesta fase; `expo-updates` fica como próximo passo natural.
5. **Duas bases de código (web + mobile)** — mitigado mantendo `services/` idêntico e mudanças de contrato feitas uma vez no backend (ADR 0001).

## Referências

- Spec do PWA: `docs/superpowers/specs/2026-09-09-poupix-pwa-design.md`
- ADRs: `docs/adr/0001-app-android-react-native-expo.md`, `docs/adr/0002-offline-somente-leitura.md`
- Plano: `docs/plans/2026-10-01-app-android.md`
