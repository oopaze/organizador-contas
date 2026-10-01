# Poupix — app Android

App nativo (React Native + Expo) do Poupix. Consome a API de produção em `https://api.poupix.connectakit.com.br`.

## Rodar

```bash
npm install
npm start
```

Com um aparelho Android: abra no Expo Go ou gere um development build (`npx expo run:android`).

## Verificação

```bash
npx tsc --noEmit
npm test
```

## Build do APK

Build local com Gradle (sem EAS):

```bash
./scripts/build-apk.sh
```

O APK sai em `mobile/builds/poupix-<versao>.apk`. O keystore de release vive fora do git (`/root/.poupix/`), com as senhas em `mobile/.secrets/keystore.env` — nenhum dos dois é versionado. Instruções completas chegam na Task 11 do plano.

## Escopo

- Leitura offline por cache local; escrita exige conexão (ADR 0002).
- O frontend web e o backend **não** são alterados por este projeto.
- Plano: `docs/plans/2026-10-01-app-android.md` · Spec: `docs/specs/2026-10-01-app-android-design.md`.
