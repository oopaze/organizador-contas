# mobile — app Android (Expo)

App Android nativo do Poupix. Plano: `docs/plans/2026-10-01-app-android.md`. Spec: `docs/specs/2026-10-01-app-android-design.md`.

## Regras deste projeto

- Rotas em `app/` (Expo Router); código fora de rotas em `src/`.
- Gerenciador de pacotes: **npm**. Dependência com código nativo: `npx expo install <pacote>`.
- `android/` é gerado (Continuous Native Generation) e ignorado no git — nunca editar à mão.
- Build do APK é **local** (`mobile/scripts/build-apk.sh`, Task 11); EAS é fallback, não o caminho padrão.
- Antes de declarar concluído: `npx tsc --noEmit` e `npm test` verdes.
- Testes usam a API assíncrona da RNTL v14: `await render(...)`, `await fireEvent(...)`.
- Leitura offline é cache local; escrita exige rede (ADR 0002). Não introduzir fila de escrita.

## Expo muda entre SDKs — não confie na memória

Antes de escrever código que toque API do Expo/React Native:

1. Leia a major do pacote `expo` no `package.json` (hoje: SDK 57).
2. Consulte a documentação versionada: `https://docs.expo.dev/versions/v57.0.0/`
3. Índice com correções de equívocos comuns de LLM: `https://docs.expo.dev/llms.txt`

## Comandos

```bash
npx expo install <package>  # resolve versões compatíveis com a SDK
npx expo start              # servidor de desenvolvimento
npx tsc --noEmit            # typecheck
npm test                    # jest-expo
npx expo-doctor             # diagnóstico de dependências/config
npx expo install --fix      # corrige versões incompatíveis
```
