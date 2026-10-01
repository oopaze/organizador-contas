# App Poupix para Android — Implementation Plan

> **For agentic workers:** Use a skill `dev-executar-plano` para implementar este plano task a task. Os steps usam checkbox (`- [ ]`) para tracking.

**Goal:** Portar o frontend atual do Poupix para um app Android nativo em `mobile/` (Expo), com paridade de telas, leitura offline e entrega em APK instalável.

**Architecture:** Expo managed + Expo Router; camada `services/` portada 1:1 do frontend web; leitura de dados via `@tanstack/react-query` com persistência em AsyncStorage (offline somente leitura, ADR 0002); UI em NativeWind com primitivos portados do shadcn.

**Tech Stack:** Expo SDK vigente (managed), Expo Router, NativeWind, `@tanstack/react-query` + persistência AsyncStorage, `expo-secure-store`, `expo-document-picker`, `@gorhom/bottom-sheet`, `lucide-react-native`, `react-native-gifted-charts`, `jest-expo` + `@testing-library/react-native`.

**Spec:** `docs/specs/2026-10-01-app-android-design.md`

## Global Constraints

- UI e textos em pt-BR, mesmos rótulos do PWA.
- `frontend/` e `backend/` **não são alterados** neste projeto.
- Offline **somente leitura** (ADR 0002): leitura nunca bloqueia por rede; escrita exige conexão e falha com erro honesto.
- Tokens **somente** em `expo-secure-store`; nunca em AsyncStorage.
- `EXPO_PUBLIC_API_URL` no `.env` (default `https://api.poupix.connectakit.com.br`); `USE_MOCK_API` permanece **constante de código**.
- Datas ISO `YYYY-MM-DD` **sem fuso**; dinheiro como string decimal (`"1234.56"`); formatação pt-BR só na exibição.
- Gerenciador de pacotes: **npm**; dependências com código nativo via `npx expo install`.
- Ícones reaproveitados de `frontend/public/` (`icon-192.png`, `icon-512.png`, `icon-maskable-512.png`).
- Sem OTA: cada entrega é um APK novo.
- Commits atômicos em pt-BR no formato `{verbo}: {descrição}` (sem ticket).

## Review Focus

Falhas que o spec implica e que precisam de teste na task dona:

1. **Data ISO sem fuso não desloca o dia** na fronteira de mês/virada de fuso — teste em T3.
2. **Valor monetário string com sinal** formata certo em pt-BR (`-R$ 89,90`) — teste em T3.
3. **Primeiro uso offline com cache vazio** mostra estado vazio honesto, não spinner infinito — teste em T8.
4. **403 com refresh falhando** desloga de forma limpa, sem loop de retry — teste em T2.
5. **Erro do backend em upload** (PDF com senha errada, arquivo inválido) aparece no diálogo — teste em T13.

## Sobre testes neste plano

- Toda task termina com `npx tsc --noEmit` limpo e `npm test` verde.
- Lógica (client, libs, contextos, cache) tem teste unitário em Jest com `expo-secure-store`/`fetch` mockados.
- Componentes têm render test com `@testing-library/react-native` quando o comportamento é testável sem device.
- Telas portadas: verificação de comportamento na fonte do PWA + render test do estado vazio/carregando; a validação visual final é no aparelho (T22).
- Fluxo de rede nos testes é sempre `fetch` mockado; nenhum teste toca a API de produção.

---

## Fase 1 — Fundação

### Task 1: Scaffold do projeto Expo em `mobile/`

**Files:**
- Create: `mobile/` (projeto criado pelo `create-expo-app`), `mobile/tailwind.config.js`, `mobile/metro.config.js`, `mobile/babel.config.js`, `mobile/global.css`, `mobile/nativewind-env.d.ts`, `mobile/jest.config.js` (ou chave `jest` no `package.json`), `mobile/__tests__/smoke.test.tsx`, `mobile/.gitignore`, `mobile/.env.example`, `mobile/README.md`
- Modify: `mobile/app.json`, `mobile/tsconfig.json`, `mobile/package.json`

**Interfaces:**
- Produces: projeto Expo com Expo Router e TypeScript, NativeWind configurado, alias `@/*` → `./src/*`, jest-expo rodando. Toda task seguinte assume `mobile/` como raiz de trabalho.

- [ ] **Step 1: Criar o projeto**

```bash
cd /root/projetos/organizador-contas
npx create-expo-app@latest mobile
```

O template default da SDK atual traz Expo Router + TypeScript (`mobile/app/_layout.tsx` existe). Se o template mudar, ajustar até que exista `mobile/app/_layout.tsx`.

- [ ] **Step 2: Instalar dependências de base**

```bash
cd mobile
npx expo install nativewind tailwindcss react-native-reanimated react-native-gesture-handler react-native-safe-area-context react-native-screens
npx expo install -- --save-dev jest-expo jest @types/jest @testing-library/react-native
```

- [ ] **Step 3: Configurar NativeWind**

`mobile/babel.config.js`:

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [['babel-preset-expo', { jsxImportSource: 'nativewind' }], 'nativewind/babel'],
  };
};
```

`mobile/metro.config.js`:

```js
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: './global.css' });
```

`mobile/tailwind.config.js`:

```js
module.exports = {
  content: ['./app/**/*.{ts,tsx}', './src/**/*.{ts,tsx}'],
  presets: [require('nativewind/preset')],
  theme: { extend: {} },
  plugins: [],
};
```

`mobile/global.css` com as três diretivas Tailwind:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Importar `../global.css` no topo de `mobile/app/_layout.tsx`. Criar `mobile/nativewind-env.d.ts` com `/// <reference types="nativewind/types" />`.

- [ ] **Step 4: Configurar alias e jest**

`mobile/tsconfig.json` — adicionar em `compilerOptions`:

```json
"baseUrl": ".",
"paths": { "@/*": ["./src/*"] }
```

`mobile/jest.config.js`:

```js
module.exports = {
  preset: 'jest-expo',
  setupFilesAfterEnv: [],
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@sentry/react-native|native-base|react-native-svg|nativewind|@gorhom/.*))',
  ],
};
```

- [ ] **Step 5: app.json + ícones**

`mobile/app.json` (ajustar o restante mantendo os campos da SDK):

```json
{
  "expo": {
    "name": "Poupix",
    "slug": "poupix",
    "scheme": "poupix",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon-512.png",
    "android": {
      "package": "com.poupix.app",
      "versionCode": 1,
      "adaptiveIcon": {
        "foregroundImage": "./assets/icon-maskable-512.png",
        "backgroundColor": "#059669"
      }
    }
  }
}
```

```bash
cp ../frontend/public/icon-512.png ../frontend/public/icon-maskable-512.png ../frontend/public/icon-192.png assets/
```

- [ ] **Step 6: .gitignore, .env.example e README**

`mobile/.gitignore`:

```
node_modules/
.expo/
dist/
android/
ios/
builds/
.env
.secrets/
coverage/
```

`mobile/.env.example`:

```
EXPO_PUBLIC_API_URL=https://api.poupix.connectakit.com.br
```

`mobile/README.md`: uma seção "Rodar" (`npm install`, `npm start`) e uma seção "Build do APK" (preenchida na Task 11).

- [ ] **Step 7: Smoke test**

`mobile/__tests__/smoke.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react-native';
import { Text } from 'react-native';

test('smoke', () => {
  render(<Text>Poupix</Text>);
  expect(screen.getByText('Poupix')).toBeTruthy();
});
```

Run: `npm test`
Expected: 1 passed.

- [ ] **Step 8: Typecheck e commit**

Run: `npx tsc --noEmit`
Expected: sem erros.

```bash
git add mobile
git commit -m "feat: cria projeto Expo do app Android"
```

---

### Task 2: Port dos services e client adaptado

**Files:**
- Create: `mobile/src/services/**` (cópia de `frontend/src/services/**`), `mobile/src/services/client.ts` (reescrito), `mobile/src/services/__tests__/client.test.ts`
- Modify: `mobile/src/services/index.ts` (se necessário para os paths)

**Interfaces:**
- Produces:
  - `tokenManager.getAccessToken(): Promise<string | null>`, `getRefreshToken(): Promise<string | null>`, `setTokens(access: string, refresh: string): Promise<void>`, `clearTokens(): Promise<void>`
  - `apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T>`
  - `apiUploadRequest<T>(endpoint: string, formData: FormData): Promise<T>`
  - `setSessionExpiredHandler(handler: (() => void) | null): void`
  - `class SessionExpiredError extends Error`
  - `USE_MOCK_API: boolean` (constante `false`)
- Consumes: nada (task de fundação).

- [ ] **Step 1: Copiar os services**

```bash
mkdir -p mobile/src
cp -r frontend/src/services mobile/src/services
```

Manter a estrutura idêntica (74 arquivos), incluindo `types.ts` e `mockData.ts`.

- [ ] **Step 2: Escrever os testes que falham**

`mobile/src/services/__tests__/client.test.ts`:

```ts
jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));
jest.mock('../auth/refresh', () => ({ refreshToken: jest.fn() }));

import * as SecureStore from 'expo-secure-store';
import { refreshToken } from '../auth/refresh';
import {
  apiRequest,
  setSessionExpiredHandler,
  SessionExpiredError,
  tokenManager,
} from '../client';

const mockedSecureStore = SecureStore as jest.Mocked<typeof SecureStore>;
const mockedRefresh = refreshToken as jest.Mock;

describe('apiRequest', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedSecureStore.getItemAsync.mockResolvedValue('token-abc');
  });

  test('envia Authorization com o token', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ ok: 1 }),
    }) as jest.Mock;

    await apiRequest('/transactions/transactions/');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/transactions/transactions/'),
      expect.objectContaining({
        headers: expect.any(Headers),
      })
    );
    const headers = (global.fetch as jest.Mock).mock.calls[0][1].headers as Headers;
    expect(headers.get('Authorization')).toBe('Bearer token-abc');
  });

  test('em 403 renova o token e repete a request', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 403, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ value: 7 }) }) as jest.Mock;
    mockedRefresh.mockResolvedValue(true);

    const result = await apiRequest('/x');

    expect(result).toEqual({ value: 7 });
    expect(mockedRefresh).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  test('refresh falhando limpa tokens, chama handler e lança SessionExpiredError', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({}),
    }) as jest.Mock;
    mockedRefresh.mockResolvedValue(false);
    const handler = jest.fn();
    setSessionExpiredHandler(handler);

    await expect(apiRequest('/x')).rejects.toBeInstanceOf(SessionExpiredError);

    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith('access_token');
    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith('refresh_token');
    expect(handler).toHaveBeenCalledTimes(1);
    setSessionExpiredHandler(null);
  });

  test('204 devolve objeto vazio', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => ({}),
    }) as jest.Mock;

    await expect(apiRequest('/x')).resolves.toEqual({});
  });
});
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `cd mobile && npx jest src/services/__tests__/client.test.ts`
Expected: FAIL (o `client.ts` copiado usa `localStorage`).

- [ ] **Step 4: Reescrever `mobile/src/services/client.ts`**

```ts
import * as SecureStore from 'expo-secure-store';

// Toggle this to switch between mock and real API
export const USE_MOCK_API = false;

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || 'https://api.poupix.connectakit.com.br';

let sessionExpiredHandler: (() => void) | null = null;

export function setSessionExpiredHandler(handler: (() => void) | null) {
  sessionExpiredHandler = handler;
}

export class SessionExpiredError extends Error {
  constructor() {
    super('Session expired');
    this.name = 'SessionExpiredError';
  }
}

const accessKey = () => (USE_MOCK_API ? 'mock_access_token' : 'access_token');
const refreshKey = () => (USE_MOCK_API ? 'mock_refresh_token' : 'refresh_token');

export const tokenManager = {
  getAccessToken: (): Promise<string | null> => SecureStore.getItemAsync(accessKey()),
  getRefreshToken: (): Promise<string | null> => SecureStore.getItemAsync(refreshKey()),
  setTokens: async (accessToken: string, refreshToken: string) => {
    await SecureStore.setItemAsync(accessKey(), accessToken);
    await SecureStore.setItemAsync(refreshKey(), refreshToken);
  },
  clearTokens: async () => {
    await SecureStore.deleteItemAsync(accessKey());
    await SecureStore.deleteItemAsync(refreshKey());
  },
};

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = await tokenManager.getAccessToken();
  const isFormData = options.body instanceof FormData;
  const headers = new Headers(
    isFormData ? {} : { 'Content-Type': 'application/json' }
  );

  if (options.headers) {
    const optionHeaders = new Headers(options.headers);
    optionHeaders.forEach((value, key) => headers.set(key, value));
  }
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

  if (!response.ok) {
    if (response.status === 403) {
      const { refreshToken } = await import('./auth/refresh');
      const refreshed = await refreshToken();
      if (refreshed) return apiRequest<T>(endpoint, options);
      await tokenManager.clearTokens();
      sessionExpiredHandler?.();
      throw new SessionExpiredError();
    }
    const data = await response.json().catch(() => ({}));
    const err = new Error(
      data.detail || data.error_description || data.error || 'An error occurred'
    ) as Error & { response?: { status: number; data: Record<string, unknown> } };
    err.response = { status: response.status, data };
    throw err;
  }

  if (response.status === 204) return {} as T;
  return response.json();
}

export async function apiUploadRequest<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const token = await tokenManager.getAccessToken();
  const headers: HeadersInit = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const err = new Error(
      data.detail || data.error || 'Upload failed'
    ) as Error & { response?: { status: number; data: Record<string, unknown> } };
    err.response = { status: response.status, data };
    throw err;
  }

  return response.json();
}
```

Ajustar `frontend/src/services/auth/refresh.ts` portado para usar `tokenManager` assíncrono (ele já importa de `../client`, então só conferir `await`).

- [ ] **Step 5: Rodar os testes**

Run: `npx jest src/services/__tests__/client.test.ts`
Expected: 4 passed.

- [ ] **Step 6: Typecheck e commit**

Run: `npx tsc --noEmit`

```bash
git add mobile/src/services
git commit -m "feat: porta camada de services com tokens em SecureStore"
```

---

### Task 3: Utilitários de formatação, data e cores

**Files:**
- Create: `mobile/src/lib/format.ts`, `mobile/src/lib/date.ts`, `mobile/src/lib/category-colors.ts` (cópia de `frontend/src/lib/category-colors.ts`), `mobile/src/lib/__tests__/format.test.ts`, `mobile/src/lib/__tests__/date.test.ts`

**Interfaces:**
- Produces:
  - `formatCurrency(value: string | number): string` — pt-BR, com sinal (`-R$ 89,90`)
  - `formatPercent(value: number): string`
  - `parseIsoDate(iso: string): Date` — meia-noite **local**, nunca UTC
  - `toIsoDate(date: Date): string` — `YYYY-MM-DD` local
  - `formatMonthYear(date: Date): string` — `"outubro de 2026"`

- [ ] **Step 1: Escrever os testes que falham**

`mobile/src/lib/__tests__/format.test.ts`:

```ts
import { formatCurrency } from '../format';

test('formata valores string em pt-BR', () => {
  expect(formatCurrency('1234.56')).toBe('R$ 1.234,56');
  expect(formatCurrency('89.9')).toBe('R$ 89,90');
  expect(formatCurrency(0)).toBe('R$ 0,00');
});

test('formata valores negativos com sinal', () => {
  expect(formatCurrency('-89.9')).toBe('-R$ 89,90');
});
```

`mobile/src/lib/__tests__/date.test.ts`:

```ts
import { parseIsoDate, toIsoDate } from '../date';

test('parseIsoDate não desloca o dia na virada de mês', () => {
  const date = parseIsoDate('2026-10-01');
  expect(date.getDate()).toBe(1);
  expect(date.getMonth()).toBe(9);
  expect(date.getFullYear()).toBe(2026);
});

test('toIsoDate devolve data local sem UTC', () => {
  expect(toIsoDate(new Date(2026, 9, 1, 23, 30))).toBe('2026-10-01');
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/lib`
Expected: FAIL (módulos não existem).

- [ ] **Step 3: Implementar**

`mobile/src/lib/format.ts`:

```ts
export function formatCurrency(value: string | number): string {
  const numeric = typeof value === 'string' ? parseFloat(value) : value;
  if (Number.isNaN(numeric)) return 'R$ 0,00';
  return numeric.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
}

export function formatPercent(value: number): string {
  return `${value.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`;
}
```

`mobile/src/lib/date.ts`:

```ts
export function parseIsoDate(iso: string): Date {
  const [year, month, day] = iso.split('-').map(Number);
  return new Date(year, month - 1, day);
}

export function toIsoDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

export function formatMonthYear(date: Date): string {
  return date.toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' });
}
```

Copiar `frontend/src/lib/category-colors.ts` sem alterações.

- [ ] **Step 4: Rodar os testes**

Run: `npx jest src/lib`
Expected: 4 passed.

- [ ] **Step 5: Typecheck e commit**

```bash
git add mobile/src/lib
git commit -m "feat: adiciona utilitários de formatação, data local e cores"
```

---

### Task 4: Primitivos de formulário

**Files:**
- Create: `mobile/src/components/ui/{button,input,label,checkbox,textarea,radio-group,switch}.tsx`, `mobile/src/components/ui/__tests__/button.test.tsx`, `mobile/src/components/ui/__tests__/input.test.tsx`, `mobile/src/components/ui/__tests__/switch.test.tsx`, `mobile/src/components/ui/utils.ts` (cópia do `cn` de `frontend/src/app/components/ui/utils.ts`, com `clsx` + `tailwind-merge`)

**Interfaces:**
- Produces:
  - `<Button variant?: 'default'|'outline'|'ghost'|'destructive', size?: 'default'|'sm'|'lg'|'icon', disabled?, onPress?, children />`
  - `<Input value onChangeText placeholder secureTextEntry keyboardType />`
  - `<Label>{children}</Label>`, `<Textarea />`, `<Checkbox checked onCheckedChange />`, `<RadioGroup value onValueChange>`, `<Switch value onValueChange />`
- Consumes: NativeWind (Task 1).

- [ ] **Step 1: Instalar dependências**

```bash
cd mobile
npm install clsx tailwind-merge
```

- [ ] **Step 2: Escrever os testes que falham**

`mobile/src/components/ui/__tests__/button.test.tsx`:

```tsx
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Button } from '../button';

test('dispara onPress quando não está desabilitado', () => {
  const onPress = jest.fn();
  render(<Button onPress={onPress}>Salvar</Button>);
  fireEvent.press(screen.getByText('Salvar'));
  expect(onPress).toHaveBeenCalledTimes(1);
});

test('não dispara onPress quando desabilitado', () => {
  const onPress = jest.fn();
  render(<Button disabled onPress={onPress}>Salvar</Button>);
  fireEvent.press(screen.getByText('Salvar'));
  expect(onPress).not.toHaveBeenCalled();
});
```

`mobile/src/components/ui/__tests__/input.test.tsx`:

```tsx
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Input } from '../input';

test('mostra label e emite o texto digitado', () => {
  const onChangeText = jest.fn();
  render(<Input label="Valor" onChangeText={onChangeText} />);
  fireEvent.changeText(screen.getByLabelText('Valor'), '54,90');
  expect(onChangeText).toHaveBeenCalledWith('54,90');
});
```

`mobile/src/components/ui/__tests__/switch.test.tsx`:

```tsx
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Switch } from '../switch';

test('inverte o valor ao tocar', () => {
  const onValueChange = jest.fn();
  render(<Switch value={false} onValueChange={onValueChange} accessibilityLabel="Modo On" />);
  fireEvent(screen.getByLabelText('Modo On'), 'valueChange', true);
  expect(onValueChange).toHaveBeenCalledWith(true);
});
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `npx jest src/components/ui`
Expected: FAIL.

- [ ] **Step 4: Implementar os primitivos**

Cada arquivo segue o desenho do equivalente em `frontend/src/app/components/ui/`, trocando elementos DOM por primitivos RN e mantendo as mesmas variantes:

```tsx
// mobile/src/components/ui/button.tsx
import { Pressable, Text, type PressableProps } from 'react-native';
import { cn } from './utils';

type Variant = 'default' | 'outline' | 'ghost' | 'destructive';
type Size = 'default' | 'sm' | 'lg' | 'icon';

const variantClasses: Record<Variant, string> = {
  default: 'bg-emerald-600 active:bg-emerald-700',
  outline: 'border border-zinc-300 bg-white active:bg-zinc-100',
  ghost: 'bg-transparent active:bg-zinc-100',
  destructive: 'bg-red-600 active:bg-red-700',
};

const textClasses: Record<Variant, string> = {
  default: 'text-white',
  outline: 'text-zinc-900',
  ghost: 'text-zinc-900',
  destructive: 'text-white',
};

const sizeClasses: Record<Size, string> = {
  default: 'h-11 px-4',
  sm: 'h-9 px-3',
  lg: 'h-12 px-6',
  icon: 'h-11 w-11',
};

export interface ButtonProps extends PressableProps {
  variant?: Variant;
  size?: Size;
  children: React.ReactNode;
}

export function Button({ variant = 'default', size = 'default', className, children, ...props }: ButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      className={cn(
        'flex-row items-center justify-center gap-2 rounded-md',
        variantClasses[variant],
        sizeClasses[size],
        props.disabled && 'opacity-50',
        className
      )}
      {...props}
    >
      {typeof children === 'string' ? (
        <Text className={cn('text-base font-medium', textClasses[variant])}>{children}</Text>
      ) : (
        children
      )}
    </Pressable>
  );
}
```

Input com label acessível (`accessibilityLabel` igual ao label, para o teste), Textarea multi-line, Checkbox com `Pressable` + ícone `Check` de `lucide-react-native`, RadioGroup com contexto próprio, Switch embrulha o `Switch` do RN com `onValueChange`. Instalar `lucide-react-native` e `react-native-svg`:

```bash
npx expo install react-native-svg
npm install lucide-react-native
```

- [ ] **Step 5: Rodar os testes**

Run: `npx jest src/components/ui`
Expected: 4 passed.

- [ ] **Step 6: Typecheck e commit**

```bash
git add mobile/src/components/ui mobile/package.json mobile/package-lock.json
git commit -m "feat: adiciona primitivos de formulário do app"
```

---

### Task 5: Primitivos de exibição

**Files:**
- Create: `mobile/src/components/ui/{card,badge,skeleton,collapsible,tabs,scroll-area}.tsx`, `mobile/src/components/ui/__tests__/card.test.tsx`, `mobile/src/components/ui/__tests__/collapsible.test.tsx`

**Interfaces:**
- Produces:
  - `<Card><CardHeader><CardTitle/><CardDescription/></CardHeader><CardContent/></Card>`
  - `<Badge variant?>{children}</Badge>`, `<Skeleton className />`, `<Collapsible open onOpenChange>{children}</Collapsible>`, `<Tabs value onValueChange>` + `<TabsList><TabsTrigger value/></TabsList><TabsContent value/>`
  - `scroll-area` vira re-export de `ScrollView`/`FlatList` não é necessário — **não criar**; usar RN direto nas telas (YAGNI).

- [ ] **Step 1: Escrever os testes que falham**

`mobile/src/components/ui/__tests__/card.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react-native';
import { Card, CardContent, CardTitle } from '../card';

test('renderiza título e conteúdo', () => {
  render(
    <Card>
      <CardTitle>Saldo</CardTitle>
      <CardContent>R$ 1.000,00</CardContent>
    </Card>
  );
  expect(screen.getByText('Saldo')).toBeTruthy();
  expect(screen.getByText('R$ 1.000,00')).toBeTruthy();
});
```

`mobile/src/components/ui/__tests__/collapsible.test.tsx`:

```tsx
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Collapsible } from '../collapsible';

test('mostra conteúdo só quando aberto', () => {
  render(
    <Collapsible open onOpenChange={() => {}} trigger={<></>}>
      <Text>Pagamentos</Text>
    </Collapsible>
  );
  expect(screen.getByText('Pagamentos')).toBeTruthy();
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/ui`
Expected: FAIL.

- [ ] **Step 3: Implementar**

Portes diretos de `frontend/src/app/components/ui/{card,badge,skeleton,collapsible,tabs}.tsx` para `View`/`Text`/`Pressable` com as mesmas classes visuais (NativeWind) e mesmas props. `Collapsible` usa estado controlado (`open` + `onOpenChange`) e o `trigger` como cabeça.

- [ ] **Step 4: Rodar os testes**

Run: `npx jest src/components/ui`
Expected: todos passam.

- [ ] **Step 5: Typecheck e commit**

```bash
git add mobile/src/components/ui
git commit -m "feat: adiciona primitivos de exibição do app"
```

---

### Task 6: Overlays (dialog, confirmação, bottom sheet, select, dropdown, popover)

**Files:**
- Create: `mobile/src/components/ui/{dialog,alert-dialog,sheet,select,dropdown-menu,popover}.tsx`, `mobile/src/components/ui/__tests__/dialog.test.tsx`, `mobile/src/components/ui/__tests__/select.test.tsx`

**Interfaces:**
- Produces:
  - `<Dialog visible onClose title description footer>{children}</Dialog>`
  - `<AlertDialog visible onConfirm onCancel title description confirmLabel cancelLabel destructive />`
  - `<Sheet visible onClose title>{children}</Sheet>` (estilo bottom sheet)
  - `<Select value onValueChange options={[{value,label}]} placeholder />` (abre a lista em bottom sheet)
  - `<DropdownMenu items={[{label, onPress, destructive?}]} trigger={<Button/>} />`
  - `<Popover trigger>{children}</Popover>` — usado no seletor de mês
- Consumes: `@gorhom/bottom-sheet`, `react-native-reanimated`, `react-native-gesture-handler` (Task 1).

- [ ] **Step 1: Instalar dependências**

```bash
cd mobile
npx expo install @gorhom/bottom-sheet
```

Garantir `react-native-reanimated/plugin` no fim do `babel.config.js` (a SDK atual pode já incluir via `babel-preset-expo`; se o bottom sheet reclamar, adicionar o plugin).

- [ ] **Step 2: Escrever os testes que falham**

`mobile/src/components/ui/__tests__/dialog.test.tsx`:

```tsx
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Button } from '../button';
import { Dialog } from '../dialog';

test('mostra conteúdo quando visível e fecha no botão', () => {
  const onClose = jest.fn();
  render(
    <Dialog visible onClose={onClose} title="Nova transação">
      <Button onPress={onClose}>Fechar</Button>
    </Dialog>
  );
  expect(screen.getByText('Nova transação')).toBeTruthy();
  fireEvent.press(screen.getByText('Fechar'));
  expect(onClose).toHaveBeenCalled();
});
```

`mobile/src/components/ui/__tests__/select.test.tsx`:

```tsx
import { fireEvent, render, screen } from '@testing-library/react-native';
import { Select } from '../select';

test('mostra o label selecionado e emite a escolha', () => {
  const onValueChange = jest.fn();
  render(
    <Select
      value="cash"
      onValueChange={onValueChange}
      options={[
        { value: 'cash', label: 'Dinheiro' },
        { value: 'credit', label: 'Cartão' },
      ]}
    />
  );
  expect(screen.getByText('Dinheiro')).toBeTruthy();
  fireEvent.press(screen.getByText('Dinheiro'));
  fireEvent.press(screen.getByText('Cartão'));
  expect(onValueChange).toHaveBeenCalledWith('credit');
});
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `npx jest src/components/ui`
Expected: FAIL.

- [ ] **Step 4: Implementar**

`Dialog` e `AlertDialog` em cima do `Modal` do RN (transparente, `KeyboardAvoidingView` no Android). `Sheet`/`Select`/`DropdownMenu` em cima do `BottomSheetModal` do `@gorhom/bottom-sheet`. `Popover` com `Modal` ancorado embaixo ou bottom sheet — o uso real (seletor de mês) decide; manter a API acima.

- [ ] **Step 5: Rodar os testes**

Run: `npx jest src/components/ui`
Expected: todos passam.

- [ ] **Step 6: Typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona overlays portados do shadcn"
```

---

### Task 7: Navegação e autenticação

**Files:**
- Create: `mobile/app/_layout.tsx`, `mobile/app/login.tsx`, `mobile/app/(tabs)/_layout.tsx`, `mobile/app/(tabs)/index.tsx` (placeholder), `mobile/app/(tabs)/planning.tsx`, `mobile/app/(tabs)/loans.tsx`, `mobile/app/(tabs)/actors.tsx`, `mobile/app/(tabs)/more.tsx`, `mobile/src/contexts/auth-context.tsx`, `mobile/src/contexts/user-context.tsx`, `mobile/src/lib/auth-guard.ts`, `mobile/src/contexts/__tests__/auth-context.test.tsx`, `mobile/src/lib/__tests__/auth-guard.test.ts`

**Interfaces:**
- Consumes: `login`, `getCurrentUser` (Task 2); `setSessionExpiredHandler` (Task 2).
- Produces:
  - `<AuthProvider>` com `useAuth(): { user, loading, login(email, password), logout() }`
  - `<UserProvider>` com `useUser(): { user, refetchUser() }`
  - `shouldRedirectToLogin(isAuthenticated: boolean, isLoading: boolean, inAuthGroup: boolean): boolean`

- [ ] **Step 1: Escrever os testes que falham**

`mobile/src/lib/__tests__/auth-guard.test.ts`:

```ts
import { shouldRedirectToLogin } from '../auth-guard';

test('redireciona para login quando resolvido e sem usuário', () => {
  expect(shouldRedirectToLogin(false, false, false)).toBe(true);
});

test('não redireciona enquanto carrega nem quando já está no login', () => {
  expect(shouldRedirectToLogin(false, true, false)).toBe(false);
  expect(shouldRedirectToLogin(false, false, true)).toBe(false);
});
```

`mobile/src/contexts/__tests__/auth-context.test.tsx`:

```tsx
jest.mock('../../services', () => ({
  login: jest.fn(),
  getCurrentUser: jest.fn(),
  tokenManager: { clearTokens: jest.fn(), setTokens: jest.fn() },
  setSessionExpiredHandler: jest.fn(),
}));

import { act, renderHook, waitFor } from '@testing-library/react-native';
import { getCurrentUser, login } from '../../services';
import { AuthProvider, useAuth } from '../auth-context';

const mockedLogin = login as jest.Mock;
const mockedGetCurrentUser = getCurrentUser as jest.Mock;

function wrapper({ children }: { children: React.ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}

test('login guarda o usuário', async () => {
  mockedGetCurrentUser.mockRejectedValue(new Error('no session'));
  mockedLogin.mockResolvedValue({
    access_token: 'a',
    refresh_token: 'r',
    user: { id: 1, email: 'eu@ex.com' },
  });

  const { result } = renderHook(() => useAuth(), { wrapper });
  await waitFor(() => expect(result.current.loading).toBe(false));

  await act(async () => {
    await result.current.login('eu@ex.com', 'senha');
  });

  expect(result.current.user).toEqual({ id: 1, email: 'eu@ex.com' });
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/lib/__tests__/auth-guard.test.ts src/contexts`
Expected: FAIL.

- [ ] **Step 3: Implementar contexto e guard**

Portar `frontend/src/contexts/{auth-context,user-context}.tsx` para os serviços assíncronos. No `_layout.tsx`, registrar o handler:

```tsx
useEffect(() => {
  setSessionExpiredHandler(() => {
    router.replace('/login');
  });
  return () => setSessionExpiredHandler(null);
}, []);
```

O guard vive em `mobile/src/lib/auth-guard.ts` como função pura (testável) e é usado em `_layout.tsx` com `useSegments()` + `useEffect` para `router.replace`.

- [ ] **Step 4: Telas de navegação**

- `app/_layout.tsx`: `GestureHandlerRootView` → `SafeAreaProvider` → `AuthProvider` → `UserProvider` → `Stack` (login sem header; tabs sem header).
- `(tabs)/_layout.tsx`: `Tabs` com 5 abas em pt-BR (Início, Planejamento, Empréstimos, Atores, Mais), ícones `lucide-react-native` (`Home`, `Target`, `HandCoins`, `Users`, `Menu`).
- `login.tsx`: porte de `frontend/src/app/components/login-page.tsx` (form, erro, loading).
- `more.tsx`: lista Conectores, Chat IA, Insights IA, Configurações e Sair (navega e chama `logout`).
- Demais telas de tab: placeholder com o título (preenchidas nas tasks seguintes).

- [ ] **Step 5: Rodar os testes**

Run: `npx jest`
Expected: todos passam.

- [ ] **Step 6: Typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona navegação por abas e autenticação"
```

---

### Task 8: Camada de dados offline (react-query + persistência)

**Files:**
- Create: `mobile/src/lib/query-client.ts`, `mobile/src/lib/use-online-status.ts`, `mobile/src/components/offline-banner.tsx`, `mobile/src/components/empty-state.tsx`, `mobile/src/lib/__tests__/query-client.test.ts`, `mobile/src/components/__tests__/offline-banner.test.tsx`, `mobile/src/components/__tests__/empty-state.test.tsx`
- Modify: `mobile/app/_layout.tsx` (envolver com `PersistQueryClientProvider`)

**Interfaces:**
- Produces:
  - `queryClient: QueryClient` (staleTime 30s, gcTime Infinity, retry 1)
  - `persister` (AsyncStorage, key `poupix-query-cache`)
  - `useOnlineStatus(): boolean`
  - `<OfflineBanner persistedAt={number | null} />` — texto: sem dados salvos → "Sem conexão — sem dados salvos ainda"; com → "Sem conexão — dados de HH:mm"
  - `<EmptyState title description action? />`
- Consumes: Task 1 (AsyncStorage), Task 7 (`_layout`).

- [ ] **Step 1: Instalar dependências**

```bash
cd mobile
npx expo install @react-native-async-storage/async-storage @react-native-community/netinfo
npm install @tanstack/react-query @tanstack/query-async-storage-persister @tanstack/react-query-persist-client
```

- [ ] **Step 2: Escrever os testes que falham**

`mobile/src/components/__tests__/offline-banner.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react-native';
import { OfflineBanner } from '../offline-banner';

test('sem cache salvo, avisa que não há dados', () => {
  render(<OfflineBanner persistedAt={null} />);
  expect(screen.getByText('Sem conexão — sem dados salvos ainda')).toBeTruthy();
});

test('com cache salvo, mostra o horário dos dados', () => {
  const timestamp = new Date(2026, 9, 1, 14, 5).getTime();
  render(<OfflineBanner persistedAt={timestamp} />);
  expect(screen.getByText('Sem conexão — dados de 14:05')).toBeTruthy();
});
```

`mobile/src/lib/__tests__/query-client.test.ts`:

```ts
import { queryClient } from '../query-client';

test('mantém o cache na memória para leitura offline', () => {
  const options = queryClient.getDefaultOptions().queries;
  expect(options?.gcTime).toBe(Infinity);
  expect(options?.staleTime).toBe(30_000);
});
```

`mobile/src/components/__tests__/empty-state.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react-native';
import { EmptyState } from '../empty-state';

test('renderiza título e descrição', () => {
  render(<EmptyState title="Nada por aqui" description="Sem lançamentos neste mês" />);
  expect(screen.getByText('Nada por aqui')).toBeTruthy();
  expect(screen.getByText('Sem lançamentos neste mês')).toBeTruthy();
});
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `npx jest src/components src/lib`
Expected: FAIL.

- [ ] **Step 4: Implementar**

`query-client.ts`:

```ts
import AsyncStorage from '@react-native-async-storage/async-storage';
import { QueryClient } from '@tanstack/react-query';
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, gcTime: Infinity, retry: 1 },
  },
});

export const persister = createAsyncStoragePersister({
  storage: AsyncStorage,
  key: 'poupix-query-cache',
  throttleTime: 1000,
});
```

`use-online-status.ts` usa `useNetInfo()` do `@react-native-community/netinfo` (`isConnected !== false`).

`OfflineBanner` usa `formatHHmm` de `src/lib/date.ts` e só renderiza quando offline. O `persistedAt` vem do `_layout`: no mount, `AsyncStorage.getItem('poupix-query-cache')` → `JSON.parse(...).timestamp` (campo gravado pelo persister); após cada persist, o `persistOptions.onSuccess` atualiza o estado que desce por prop.

`EmptyState` é o componente padrão de lista vazia, usado por todas as telas.

- [ ] **Step 5: Envolver o app no provider persistido**

Em `mobile/app/_layout.tsx`:

```tsx
<PersistQueryClientProvider client={queryClient} persistOptions={{ persister }}>
  <OfflineBanner ... />
  {/* resto */}
</PersistQueryClientProvider>
```

- [ ] **Step 6: Rodar os testes e typecheck**

Run: `npx jest && npx tsc --noEmit`
Expected: tudo verde.

- [ ] **Step 7: Commit**

```bash
git add mobile
git commit -m "feat: adiciona cache persistido e estado offline"
```

---

## Fase 2 — Núcleo financeiro (Modo On)

### Task 9: Tela Início — cards, mês e abas

**Files:**
- Modify: `mobile/app/(tabs)/index.tsx`
- Create: `mobile/src/components/month-picker.tsx`, `mobile/src/components/stat-card.tsx`, `mobile/src/components/__tests__/stat-card.test.tsx`

**Interfaces:**
- Consumes: `getTransactionStats`, `getLedger`, `ensureSalary`, `ensureCardBills` (Task 2); `useUser` (Task 7); react-query (Task 8).
- Produces: `<StatCard title value subtitle icon tone />`; `<MonthPicker value onChange />` (bottom sheet com 12 meses + navegação de ano).

Fonte de comportamento: `frontend/src/app/pages/dashboard-page.tsx` (cards Saldo, Receitas, Despesas, A Receber; card de metas com percentual; legenda de categorias com valores; seletor de mês; toggle "incluir não pagos"; abas Extrato/Lançamentos quando `modoOn`).

- [ ] **Step 1: Teste do StatCard**

`mobile/src/components/__tests__/stat-card.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react-native';
import { StatCard } from '../stat-card';

test('mostra título, valor e subtítulo', () => {
  render(<StatCard title="Saldo" value="R$ 1.234,56" subtitle="outubro" />);
  expect(screen.getByText('Saldo')).toBeTruthy();
  expect(screen.getByText('R$ 1.234,56')).toBeTruthy();
  expect(screen.getByText('outubro')).toBeTruthy();
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/stat-card.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implementar StatCard e MonthPicker**

Portar a marcação dos cards do dashboard web (título pequeno, valor grande, ícone tonalizado) e o seletor de mês como `Popover`/bottom sheet (Task 6).

- [ ] **Step 4: Montar a tela**

Montar `app/(tabs)/index.tsx` com `useQuery` por recurso (chaves `['transactions', filtros]`, `['stats', filtros]`, `['ledger', filtros]`), carregando em paralelo; `modoOn` do `useUser()` decide entre abas Extrato/Lançamentos; `ensureSalary`/`ensureCardBills` no mount como no web; estados: carregando (Skeleton), erro de rede com dados antigos (OfflineBanner), vazio (`EmptyState`), e refresh por pull-to-refresh.

- [ ] **Step 5: Rodar testes, typecheck e commit**

Run: `npx jest && npx tsc --noEmit`

```bash
git add mobile
git commit -m "feat: monta tela Início com cards e seletor de mês"
```

---

### Task 10: Listas — extrato, transações, subs e pagamento

**Files:**
- Create: `mobile/src/components/{ledger-list,transactions-list,sub-transactions-list}.tsx`, `mobile/src/components/__tests__/ledger-list.test.tsx`
- Modify: `mobile/app/(tabs)/index.tsx`

**Interfaces:**
- Consumes: `getLedger`, `getTransactions`, `getSubTransactions`, `payTransaction`, `paySubTransaction`, `deleteTransaction`, `deleteSubTransaction` (Task 2); formatação (Task 3); overlays/confirmação (Task 6).
- Produces: `LedgerList({ ledger })`, `TransactionsList({ transactions, onChanged })`, `SubTransactionsList({ subTransactions, onChanged })` — todos em cards (`FlatList`), com ação de pagar e apagar (com confirmação).

Fonte: `frontend/src/app/components/{ledger-list,transactions-list,sub-transactions-table}.tsx` — a tabela vira lista de cards com as mesmas informações (descrição, valor, categoria com cor, data, pago/não pago, ator, parcelas).

- [ ] **Step 1: Teste do LedgerList**

`mobile/src/components/__tests__/ledger-list.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react-native';
import { LedgerList } from '../ledger-list';

test('mostra entradas do extrato com valor formatado', () => {
  render(
    <LedgerList
      ledger={{
        entries: [
          {
            id: 1,
            description: 'Padaria',
            amount: '-18.50',
            date: '2026-10-01',
            transaction_type: 'outgoing',
            paid: true,
          } as never,
        ],
        summary: { realized: '-18.50', forecast: '-18.50' } as never,
      }}
    />
  );
  expect(screen.getByText('Padaria')).toBeTruthy();
  expect(screen.getByText(/-R\$\s?18,50/)).toBeTruthy();
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/ledger-list.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implementar as listas**

Padrões: card com linha de valor à direita, cor por categoria (`category-colors.ts`), estado pago com ícone `CheckCircle2`, ações em `DropdownMenu` (pagar, editar, apagar), confirmação via `AlertDialog` para apagar. Pull-to-refresh e `onEndReached` quando a lista web paginar.

- [ ] **Step 4: Ligar na tela Início**

Substituir os placeholders da Task 9 pelas listas; ao pagar/apagar, invalidar `['transactions']`, `['stats']`, `['ledger']` e refetch.

- [ ] **Step 5: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona listas de extrato, transações e subs"
```

---

### Task 11: Primeiro APK (milestone)

**Files:**
- Create: `mobile/scripts/build-apk.sh`, `mobile/builds/.gitkeep`
- Modify: `mobile/README.md` (seção Build do APK)

**Interfaces:**
- Produces: `mobile/builds/poupix-<versao>.apk` instalável; script `npm run build:apk`.

- [ ] **Step 1: Instalar toolchain nesta máquina**

```bash
apt-get update && apt-get install -y openjdk-17-jdk-headless unzip
mkdir -p /opt/android-sdk/cmdline-tools
cd /tmp && curl -LO https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip -q commandlinetools-linux-11076708_latest.zip -d /opt/android-sdk/cmdline-tools
mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest
export ANDROID_HOME=/opt/android-sdk
yes | /opt/android-sdk/cmdline-tools/latest/bin/sdkmanager --licenses
/opt/android-sdk/cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-35" "build-tools;35.0.0"
```

Registrar `ANDROID_HOME` e `PATH` no `~/.bashrc`.

- [ ] **Step 2: Gerar o keystore (fora do git)**

```bash
mkdir -p /root/.poupix mobile/.secrets
STORE_PASS=$(openssl rand -hex 16)
KEY_PASS=$(openssl rand -hex 16)
printf 'POUPIX_STORE_PASSWORD=%s\nPOUPIX_KEY_PASSWORD=%s\n' "$STORE_PASS" "$KEY_PASS" > mobile/.secrets/keystore.env
keytool -genkeypair -v -keystore /root/.poupix/poupix-release.jks -alias poupix \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass "$STORE_PASS" -keypass "$KEY_PASS" \
  -dname "CN=Poupix, OU=App, O=Poupix, L=Sao Paulo, ST=SP, C=BR"
```

As senhas ficam só em `mobile/.secrets/keystore.env` (gitignored). **Nunca commitar.**

- [ ] **Step 3: Script de build**

`mobile/scripts/build-apk.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .secrets/keystore.env
export ANDROID_HOME="${ANDROID_HOME:-/opt/android-sdk}"
VERSION=$(node -p "require('./app.json').expo.version")

npx expo prebuild -p android --clean

# assinatura de release
python3 - <<'PY'
import re, pathlib
path = pathlib.Path('android/app/build.gradle')
text = path.read_text()
signing = """
    signingConfigs {
        release {
            storeFile file(System.getenv('POUPIX_KEYSTORE') ?: '/root/.poupix/poupix-release.jks')
            storePassword System.getenv('POUPIX_STORE_PASSWORD')
            keyAlias 'poupix'
            keyPassword System.getenv('POUPIX_KEY_PASSWORD')
        }
    }
"""
if 'signingConfigs' not in text:
    text = text.replace('android {', 'android {' + signing, 1)
    text = text.replace('signingConfig signingConfigs.debug', 'signingConfig signingConfigs.release')
    path.write_text(text)
PY

cd android
./gradlew assembleRelease --no-daemon
cd ..
mkdir -p builds
cp android/app/build/outputs/apk/release/app-release.apk "builds/poupix-${VERSION}.apk"
echo "APK: mobile/builds/poupix-${VERSION}.apk"
```

```bash
chmod +x mobile/scripts/build-apk.sh
```

- [ ] **Step 4: Rodar o build**

Run: `cd mobile && ./scripts/build-apk.sh`
Expected: `mobile/builds/poupix-1.0.0.apk` gerado. Se o Gradle estourar memória (7 GB), reduzir em `android/gradle.properties`: `org.gradle.jvmargs=-Xmx2048m` e repetir; se ainda falhar, registrar o fallback EAS no README e pausar o milestone para o usuário decidir.

- [ ] **Step 5: Instalar no aparelho**

Entregar o caminho do APK ao usuário e pedir o teste: instalar (permitindo fontes desconhecidas) e fazer login. Registrar o resultado — correções viram tasks de bugfix no próprio ledger do plano.

- [ ] **Step 6: Documentar e commitar**

Atualizar `mobile/README.md` com toolchain, keystore, script e caminho do APK.

```bash
git add mobile/scripts mobile/README.md mobile/package.json mobile/app.json
git commit -m "feat: adiciona build local do APK"
```

---

### Task 12: Diálogos de transação

**Files:**
- Create: `mobile/src/components/{add-transaction-dialog,edit-transaction-dialog,add-sub-transaction-dialog,edit-sub-transaction-dialog,quick-add-dialog}.tsx`, `mobile/src/components/__tests__/add-transaction-dialog.test.tsx`
- Modify: `mobile/app/(tabs)/index.tsx` e listas (abrir diálogos, botão flutuante de lançamento rápido)

**Interfaces:**
- Consumes: `createTransaction`, `updateTransaction`, `createSubTransaction`, `updateSubTransaction`, `getActors`, `createActor`, `guessSubTransactionsCategory`, `quickAddTransaction` (Task 2); `Dialog`/`Select` (Task 6); formatação (Task 3).
- Produces: diálogos com os mesmos campos do PWA (descrição, valor, data, tipo, categoria, ator, parcelas/recorrência, pago) e o **lançamento rápido** do Modo On (dinheiro/débito/pix e cartão com fatura em aberto), num botão flutuante na tela Início.

Fonte: `frontend/src/app/components/{add-transaction-dialog,edit-transaction-dialog,add-sub-transaction-dialog,edit-sub-transaction-dialog,quick-add-dialog}.tsx`.

- [ ] **Step 1: Teste de validação do formulário**

`mobile/src/components/__tests__/add-transaction-dialog.test.tsx`:

```tsx
import { fireEvent, render, screen } from '@testing-library/react-native';
import { AddTransactionDialog } from '../add-transaction-dialog';

jest.mock('../../services', () => ({
  createTransaction: jest.fn(),
  getActors: jest.fn().mockResolvedValue([]),
  createActor: jest.fn(),
}));

test('não envia com valor inválido e mostra erro', async () => {
  const { createTransaction } = jest.requireMock('../../services');
  render(<AddTransactionDialog visible onClose={() => {}} onCreated={() => {}} />);
  fireEvent.press(screen.getByText('Salvar'));
  expect(createTransaction).not.toHaveBeenCalled();
  expect(screen.getByText('Informe um valor válido')).toBeTruthy();
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/add-transaction-dialog.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implementar os diálogos**

Portar campos e validações do web (aceitar vírgula como separador decimal, converter para string decimal com ponto antes de enviar). Manter `guessSubTransactionsCategory` no diálogo de sub como no web (com loading e erro não bloqueante).

- [ ] **Step 4: Ligar nas listas e na tela**

Botão "+" abre adicionar; menu do card abre editar; sub-transações abrem seus diálogos. Invalidar as queries afetadas ao salvar.

- [ ] **Step 5: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona diálogos de transação e subs"
```

---

### Task 13: Uploads e conciliação de fatura

**Files:**
- Create: `mobile/src/components/{upload-bill-dialog,upload-sheet-dialog,upload-pix-receipt-dialog,reconcile-bill-dialog}.tsx`, `mobile/src/components/__tests__/upload-bill-dialog.test.tsx`
- Modify: `mobile/app/(tabs)/index.tsx` (abrir uploads e conciliação)

**Interfaces:**
- Consumes: `uploadBill`, `uploadSheet`, `uploadPixReceipt`, `previewReconciliation`, `applyReconciliation` (Task 2); `expo-document-picker`; `apiUploadRequest` (Task 2).
- Produces: seleção de arquivo → `FormData` com `{ uri, name, type }` → upload; `uploadBill` devolve `transaction_ids` → abre `ReconcileBillDialog`.

Fonte: `frontend/src/app/components/{upload-bill-dialog,upload-sheet-dialog,upload-pix-receipt-dialog,reconcile-bill-dialog}.tsx`.

- [ ] **Step 1: Instalar dependência**

```bash
npx expo install expo-document-picker
```

- [ ] **Step 2: Teste do erro de upload (Review Focus 5)**

`mobile/src/components/__tests__/upload-bill-dialog.test.tsx`:

```tsx
import { fireEvent, render, screen, waitFor } from '@testing-library/react-native';
import * as DocumentPicker from 'expo-document-picker';
import { uploadBill } from '../../services';
import { UploadBillDialog } from '../upload-bill-dialog';

jest.mock('expo-document-picker', () => ({ getDocumentAsync: jest.fn() }));
jest.mock('../../services', () => ({ uploadBill: jest.fn() }));

test('mostra o erro do backend quando o upload falha', async () => {
  (DocumentPicker.getDocumentAsync as jest.Mock).mockResolvedValue({
    canceled: false,
    assets: [{ uri: 'file://f.pdf', name: 'f.pdf', mimeType: 'application/pdf', size: 10 }],
  });
  (uploadBill as jest.Mock).mockRejectedValue(new Error('PDF protegido: senha inválida'));

  render(<UploadBillDialog visible onClose={() => {}} onUploaded={() => {}} />);
  fireEvent.press(screen.getByText('Selecionar arquivo'));
  await waitFor(() => expect(screen.getByText('PDF protegido: senha inválida')).toBeTruthy());
});
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/upload-bill-dialog.test.tsx`
Expected: FAIL.

- [ ] **Step 4: Implementar**

Helper único `pickFile(mimeTypes)` em `mobile/src/lib/pick-file.ts` que devolve `{ uri, name, type, size } | null`; cada diálogo monta seu `FormData` como o web (incluindo `password`, `model`, `create_in_future_months` no de fatura). Erros do backend exibidos no diálogo (não em toast). O `reconcile-bill-dialog` recebe `transactionIds` e mostra pares conciliados com confirmação antes de aplicar.

- [ ] **Step 5: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona uploads e conciliação de fatura"
```

---

## Fase 3 — Planejamento, configurações, atores e empréstimos

### Task 14: Planejamento

**Files:**
- Create: `mobile/app/(tabs)/planning.tsx`, `mobile/src/components/{intention-dialog,intention-list}.tsx`, `mobile/src/components/__tests__/intention-list.test.tsx`

**Interfaces:**
- Consumes: `getIntentions`, `createIntention`, `updateIntention`, `deleteIntention`, `convertIntention`, `getProjection`, `getLedger`, `ensureSalary`, `ensureCardBills` (Task 2).
- Produces: tela com intenções (criar/editar/apagar/converter), projeção do período e resumo por categoria; seletor de intervalo de meses (bottom sheet, substitui o popover web).

Fonte: `frontend/src/app/pages/planning-page.tsx`.

- [ ] **Step 1: Teste da lista de intenções**

`mobile/src/components/__tests__/intention-list.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react-native';
import { IntentionList } from '../intention-list';

test('mostra intenção com valor formatado', () => {
  render(
    <IntentionList
      intentions={[
        { id: 1, title: 'Notebook', amount: '4500.00', category: 'shopping' } as never,
      ]}
      onChanged={() => {}}
    />
  );
  expect(screen.getByText('Notebook')).toBeTruthy();
  expect(screen.getByText(/R\$\s?4\.500,00/)).toBeTruthy();
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/intention-list.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implementar a tela**

Portar a página web com os mesmos blocos (formulário, lista, projeção, resumo por categoria) e as mesmas regras de período. Confirmações de converter/apagar com `AlertDialog`.

- [ ] **Step 4: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona tela de planejamento"
```

---

### Task 15: Configurações e cartões

**Files:**
- Create: `mobile/app/settings.tsx`, `mobile/src/components/card-form-dialog.tsx`, `mobile/src/components/__tests__/settings-goals.test.tsx`

**Interfaces:**
- Consumes: `getCards`, `createCard`, `updateCard`, `setCardActive`, `updateProfile` (Task 2); `Switch`/`Input` (Task 4).
- Produces: tela com salário/dia, metas percentuais (com dica em R$), toggle Modo On e CRUD de cartões (nome, dia de vencimento, ativo).

Fonte: `frontend/src/app/pages/settings-page.tsx`.

- [ ] **Step 1: Extrair a conta da dica de meta e testar**

`mobile/src/components/__tests__/settings-goals.test.tsx`:

```tsx
import { goalHint } from '../../lib/goals';

test('calcula a dica em reais a partir do salário', () => {
  expect(goalHint('30', '1000')).toBe('= R$ 300,00');
});

test('pede salário quando ele não está configurado', () => {
  expect(goalHint('30', '')).toBe('Configure o salário para ver o valor');
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/settings-goals.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implementar `src/lib/goals.ts` e a tela**

Portar os mesmos campos e o mesmo `updateProfile` (PATCH). Cartões: lista com badge ativo/inativo, `Switch` para ativar/desativar, diálogo de criar/editar.

- [ ] **Step 4: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona configurações e cartões"
```

---

### Task 16: Atores

**Files:**
- Create: `mobile/app/(tabs)/actors.tsx`, `mobile/src/components/{add-actor-dialog,edit-actor-dialog,share-actor-dialog,actor-sub-transactions-list}.tsx`, `mobile/src/components/__tests__/share-actor-dialog.test.tsx`

**Interfaces:**
- Consumes: `getActors`, `createActor`, `updateActor`, `deleteActor`, `getActorStats`, `getActorShareToken`, `getSubTransactions` (Task 2); `expo-clipboard`; `Share` do RN.
- Produces: tela de atores com cards (stats de cada ator), CRUD, sub-transações do ator e compartilhar link (`https://poupix.connectakit.com.br/share/actor?token=...`) via folha de compartilhamento + copiar.

Fonte: `frontend/src/app/pages/actors-page.tsx` e `frontend/src/app/components/{add-actor-dialog,edit-actor-dialog,share-actor-dialog,actor-sub-transactions-table}.tsx`.

- [ ] **Step 1: Instalar dependência e testar o link**

```bash
npx expo install expo-clipboard
```

`mobile/src/components/__tests__/share-actor-dialog.test.tsx`:

```tsx
jest.mock('../../services', () => ({
  getActorShareToken: jest.fn().mockResolvedValue({ token: 'abc' }),
}));

import { render, screen } from '@testing-library/react-native';
import { ShareActorDialog } from '../share-actor-dialog';

test('monta o link web do ator com o token', async () => {
  render(<ShareActorDialog visible actorId={7} onClose={() => {}} />);
  expect(await screen.findByText(/\/share\/actor\?token=abc/)).toBeTruthy();
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/share-actor-dialog.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implementar**

Portar a página e os diálogos; a URL base do link de share é fixa de produção (`https://poupix.connectakit.com.br`) — o web continua sendo o dono dessas páginas. Compartilhar com `Share.share({ message: url })` e copiar com `Clipboard.setStringAsync(url)`.

- [ ] **Step 4: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona tela de atores"
```

---

### Task 17: Empréstimos

**Files:**
- Create: `mobile/app/(tabs)/loans.tsx`, `mobile/src/components/{add-loan-dialog,edit-loan-dialog,add-loan-payment-dialog,loan-payments-list}.tsx`, `mobile/src/components/__tests__/loan-payments-list.test.tsx`

**Interfaces:**
- Consumes: `getLoans`, `getLoan`, `createLoan`, `updateLoan`, `deleteLoan`, `getLoanPayments`, `createLoanPayment`, `updateLoanPayment`, `deleteLoanPayment`, `getLoanStats`, `uploadLoanFile`, `uploadPixReceipt` (Task 2); `pickFile` (Task 13).
- Produces: tela de empréstimos com cards (saldo, pago, parcelas), CRUD, pagamentos (criar/editar/apagar) e upload de arquivo/comprovante PIX.

Fonte: `frontend/src/app/pages/loans-page.tsx` e `frontend/src/app/components/{add-loan-dialog,edit-loan-dialog,add-loan-payment-dialog,loan-payments-table}.tsx`.

- [ ] **Step 1: Teste da lista de pagamentos**

`mobile/src/components/__tests__/loan-payments-list.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react-native';
import { LoanPaymentsList } from '../loan-payments-list';

test('mostra pagamentos com valor formatado', () => {
  render(
    <LoanPaymentsList
      payments={[{ id: 1, amount: '250.00', paid_at: '2026-10-01' } as never]}
      onChanged={() => {}}
    />
  );
  expect(screen.getByText(/R\$\s?250,00/)).toBeTruthy();
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/loan-payments-list.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implementar a tela**

Portar a página e diálogos com as mesmas regras (juros/parcelas como no web) e os uploads via `pickFile`.

- [ ] **Step 4: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona tela de empréstimos"
```

---

## Fase 4 — IA e conectores

### Task 18: Chat IA

**Files:**
- Create: `mobile/app/chat.tsx`, `mobile/src/components/chat-message.tsx`, `mobile/src/components/__tests__/chat-message.test.tsx`

**Interfaces:**
- Consumes: `startChat`, `listConversations`, `getConversationMessages`, `sendMessageToConversation` (Task 2); `Select`, `Sheet` (Task 6).
- Produces: tela de chat com seleção de modelo, histórico (sheet), envio de mensagem e renderização de markdown.

Fonte: `frontend/src/app/pages/chat-page.tsx` (modelos em `AI_MODELS`, `ProviderIcon` em `frontend/src/app/components/icons/provider-icons.tsx`).

- [ ] **Step 1: Instalar renderer de markdown e testar**

```bash
npx expo install react-native-markdown-display
```

`mobile/src/components/__tests__/chat-message.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react-native';
import { ChatMessage } from '../chat-message';

test('renderiza mensagem do usuário', () => {
  render(<ChatMessage role="user" content="Quanto gastei em outubro?" />);
  expect(screen.getByText('Quanto gastei em outubro?')).toBeTruthy();
});
```

Se `react-native-markdown-display` não estiver compatível com a SDK vigente, usar renderer alternativo mantendo o contrato do componente sob teste (o teste é o contrato).

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/chat-message.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implementar a tela**

Portar seleção de modelo, sheet de conversas, layout de mensagens (bolha do usuário/IA com ícones `User`/`Bot`) e o envio otimista como no web. Teclado: `KeyboardAvoidingView` + lista invertida ou scroll para o fim ao enviar.

- [ ] **Step 4: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona tela de chat"
```

---

### Task 19: Insights IA

**Files:**
- Create: `mobile/app/ai-insights.tsx`, `mobile/src/components/{ai-calls-list,usage-chart}.tsx`, `mobile/src/lib/export-file.ts`, `mobile/src/lib/__tests__/export-file.test.ts`, `mobile/src/components/__tests__/usage-chart.test.tsx`

**Interfaces:**
- Consumes: `getAICalls`, `getAICallsStats`, `getEmbeddings`, `getEmbeddingsStats` (Task 2).
- Produces: `exportJson(filename: string, data: unknown): Promise<void>` (grava com `expo-file-system` e abre `expo-sharing`); `<UsageChart data />` com `react-native-gifted-charts`; lista de chamadas com abertura do arquivo em `Linking`.

Fonte: `frontend/src/app/pages/ai-insights-page.tsx` (download substituído por share nativo; `window.open` substituído por `Linking.openURL`).

- [ ] **Step 1: Instalar dependências e testar o export**

```bash
npx expo install expo-file-system expo-sharing
npm install react-native-gifted-charts
```

`mobile/src/lib/__tests__/export-file.test.ts`:

```ts
jest.mock('expo-file-system', () => ({
  cacheDirectory: 'file:///cache/',
  writeAsStringAsync: jest.fn().mockResolvedValue(undefined),
}));
jest.mock('expo-sharing', () => ({ shareAsync: jest.fn().mockResolvedValue(undefined) }));

import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { exportJson } from '../export-file';

test('grava o arquivo e abre o compartilhamento', async () => {
  await exportJson('ai-calls.json', [{ id: 1 }]);
  expect(FileSystem.writeAsStringAsync).toHaveBeenCalledWith(
    'file:///cache/ai-calls.json',
    JSON.stringify([{ id: 1 }])
  );
  expect(Sharing.shareAsync).toHaveBeenCalledWith('file:///cache/ai-calls.json');
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/lib/__tests__/export-file.test.ts`
Expected: FAIL.

- [ ] **Step 3: Implementar tela, gráfico e export**

Portar stats e lista; gráficos com `gifted-charts` (barras de custo/chamadas). Se a dependência conflitar no Expo, substituir por barras simples com `View` mantendo as mesmas informações — registrar a escolha no commit. Se a SDK vigente expõe a nova API do `expo-file-system` (`Paths`), ajustar teste e implementação juntos — o contrato verificável é gravar o arquivo e abrir o compartilhamento.

- [ ] **Step 4: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona insights de IA com gráficos"
```

---

### Task 20: Conectores MCP e tela Mais

**Files:**
- Create: `mobile/app/integrations.tsx`, `mobile/src/components/__tests__/more-menu.test.tsx`
- Modify: `mobile/app/(tabs)/more.tsx`

**Interfaces:**
- Consumes: `mcpConnections`, `oauthAuthorize` (Task 2); `expo-clipboard`; `expo-web-browser`.
- Produces: tela de conectores (URL do MCP, estado das conexões, copiar) e tela Mais com Conectores, Chat IA, Insights IA, Configurações, Sair.

Fonte: `frontend/src/app/pages/integrations-page.tsx` (fluxos de OAuth abrem no navegador — `WebBrowser.openBrowserAsync`; a página de consentimento continua no web).

- [ ] **Step 1: Instalar dependência e testar o menu Mais**

```bash
npx expo install expo-web-browser
```

`mobile/src/components/__tests__/more-menu.test.tsx`:

```tsx
jest.mock('expo-router', () => ({ useRouter: () => ({ push: jest.fn() }) }));

import { render, screen } from '@testing-library/react-native';
import { MoreMenu } from '../more-menu';

test('lista os destinos do menu Mais', () => {
  render(
    <MoreMenu
      onNavigate={() => {}}
      onLogout={() => {}}
      items={[
        { label: 'Conectores', route: '/integrations' },
        { label: 'Chat IA', route: '/chat' },
        { label: 'Insights IA', route: '/ai-insights' },
        { label: 'Configurações', route: '/settings' },
      ]}
    />
  );
  expect(screen.getByText('Conectores')).toBeTruthy();
  expect(screen.getByText('Configurações')).toBeTruthy();
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `npx jest src/components/__tests__/more-menu.test.tsx`
Expected: FAIL.

- [ ] **Step 3: Implementar**

Portar a página de integrações; o menu Mais vira o componente testado acima com os mesmos destinos do PWA instalado mais o que ele esconde, e o botão Sair chama `logout()` do contexto.

- [ ] **Step 4: Rodar testes, typecheck e commit**

```bash
git add mobile
git commit -m "feat: adiciona conectores e menu Mais"
```

---

## Fase 5 — Fechamento

### Task 21: Polimento de app nativo

**Files:**
- Modify: `mobile/app/**`, `mobile/src/components/dialog.tsx`, `mobile/src/components/ui/**`, `mobile/README.md`, `mobile/.env.example`

**Interfaces:**
- Consumes: tudo das tasks anteriores.

- [ ] **Step 1: Teclado e formulários**

Todo diálogo com input usa `KeyboardAvoidingView` (`behavior="padding"` no Android) e rola quando o teclado abre. Testar em device com o diálogo de transação.

- [ ] **Step 2: Botão voltar do Android**

`BackHandler`: com diálogo/sheet aberto, o voltar fecha o overlay; nas tabs, o voltar padrão do sistema (sair/voltar no stack).

- [ ] **Step 3: Acessibilidade e alvos de toque**

Todas as ações destrutivas com `accessibilityLabel` e alvo ≥ 44px (herdar decisões do PWA: `loans-page`, `actors-page`, menus, X de fechar).

- [ ] **Step 4: Estados vazios, erro e carregando**

Revisar cada tela: `Skeleton` no carregando, `EmptyState` no vazio, banner offline com dados antigos, erro de escrita com mensagem clara.

- [ ] **Step 5: README e versionamento**

`mobile/README.md`: rodar, build do APK, keystore (onde fica, como regenerar), limitações conhecidas (sem escrita offline, sem câmera). `.env.example` completo. `app.json`: `version` e `versionCode` documentados para bump.

- [ ] **Step 6: Rodar testes, typecheck e commit**

```bash
npx jest && npx tsc --noEmit
git add mobile
git commit -m "feat: polimento de teclado, back e acessibilidade"
```

---

### Task 22: Verificação final e APK de release

**Files:**
- Modify: `mobile/builds/` (artefato), `docs/specs/2026-10-01-app-android-design.md` (status), ledger de execução (`.dev-powers/`)

- [ ] **Step 1: Suíte completa**

Run: `cd mobile && npx tsc --noEmit && npm test`
Expected: tudo verde. Registrar a contagem de testes.

- [ ] **Step 2: Checklist do spec no aparelho**

Entregar o APK e acompanhar o usuário item a item do spec: instala; login contra produção; dashboard com dados; modo avião com dados salvos e banner; uploads (fatura, planilha, PIX, arquivo de empréstimo); CRUD de atores/empréstimos/pagamentos/cartões/configurações; planejamento; compartilhar link; chat/insights/conectores; escrita sem rede com erro honesto.

- [ ] **Step 3: Corrigir o que aparecer**

Cada correção vira um commit atômico próprio (`fix: ...`) e um APK novo se necessário.

- [ ] **Step 4: Commit final e PR**

Atualizar o status do spec para "Implementado" e o `README.md` do mobile se algo mudou.

```bash
git add mobile docs
git commit -m "docs: atualiza status do spec do app Android"
git push -u origin feat/app-android
```

Depois: `revisar-pr` na branch e `criar-pr` (base `main`, squash and merge conforme `AGENTS.md`).
