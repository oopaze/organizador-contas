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

Build local com Gradle (sem EAS), assinado em release. Artefato: `mobile/builds/poupix-<versao>.apk`.

```bash
cd mobile
npm run build:apk   # ou ./scripts/build-apk.sh
```

O script roda `npx expo prebuild -p android --clean`, injeta `signingConfigs.release` no `android/app/build.gradle` gerado, compila com `./android/gradlew assembleRelease --no-daemon` e copia o APK para `builds/poupix-<versao>.apk`. `android/` e regenerado a cada build (CNG) e nao e versionado.

### Toolchain

- **JDK 17** (`openjdk-17-jdk-headless`); o script deriva `JAVA_HOME` do `java` do PATH.
- **Android SDK** em `/opt/android-sdk` (default de `ANDROID_HOME` no script), com as versoes que a Expo SDK 57 / React Native 0.86 exigem (`node_modules/react-native/gradle/libs.versions.toml`):
  - `cmdline-tools` (latest)
  - `platform-tools`
  - `platforms;android-36`, `build-tools;36.0.0` (compileSdk/targetSdk 36)
  - `ndk;27.1.12297006`, `cmake;3.22.1` (compilacao dos modulos nativos)

Instalacao (uma vez):

```bash
apt-get update && apt-get install -y openjdk-17-jdk-headless unzip
mkdir -p /opt/android-sdk/cmdline-tools
curl -Lo /tmp/cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-16111833_latest.zip
unzip -q /tmp/cmdline-tools.zip -d /opt/android-sdk/cmdline-tools
mv /opt/android-sdk/cmdline-tools/cmdline-tools /opt/android-sdk/cmdline-tools/latest
export ANDROID_HOME=/opt/android-sdk
/opt/android-sdk/cmdline-tools/latest/bin/sdkmanager \
  "platform-tools" "platforms;android-36" "build-tools;36.0.0" \
  "ndk;27.1.12297006" "cmake;3.22.1"
```

A URL do `commandlinetools` e fixa por versao; a atual sai da pagina oficial (<https://developer.android.com/studio#command-tools>).

### Keystore de release

- Keystore: `/root/.poupix/poupix-release.jks` (fora do git), alias `poupix`.
- Senhas: `mobile/.secrets/keystore.env` (gitignored). O script le esse arquivo e exporta para o Gradle.

Regenerar o keystore (so se for criar uma assinatura nova — aparelhos com a chave antiga nao instalam atualizacao por cima):

```bash
mkdir -p /root/.poupix mobile/.secrets
PASS=$(openssl rand -hex 16)
printf 'POUPIX_STORE_PASSWORD=%s\nPOUPIX_KEY_PASSWORD=%s\n' "$PASS" "$PASS" > mobile/.secrets/keystore.env
chmod 600 mobile/.secrets/keystore.env
keytool -genkeypair -v -keystore /root/.poupix/poupix-release.jks -alias poupix \
  -keyalg RSA -keysize 2048 -validity 10000 -storetype PKCS12 \
  -storepass "$PASS" -keypass "$PASS" \
  -dname "CN=Poupix, OU=App, O=Poupix, L=Sao Paulo, ST=SP, C=BR"
```

Nota: o keystore e PKCS12 e usa a mesma senha para store e chave — o keytool do JDK 17 nao aceita senhas diferentes nesse formato. Variaveis aceitas pelo script: `POUPIX_KEYSTORE`, `POUPIX_KEY_ALIAS`, `POUPIX_ARCHS`.

### Verificar o artefato

```bash
unzip -l mobile/builds/poupix-1.0.0.apk | head
/opt/android-sdk/build-tools/36.0.0/apksigner verify --print-certs mobile/builds/poupix-1.0.0.apk
```

### Memoria

Esta maquina tem 8 GB, 4 vCPUs e **sem swap**. O script limita o build para nao estourar a memoria: `-Dorg.gradle.workers.max=2` e `-Dkotlin.daemon.jvmargs=-Xmx1024m`, mantendo `org.gradle.jvmargs=-Xmx2048m -XX:MaxMetaspaceSize=512m`. Se o build rodar em maquina maior, esses limites podem ser afrouxados.

## Escopo

- Leitura offline por cache local; escrita exige conexão (ADR 0002).
- O frontend web e o backend **não** são alterados por este projeto.
- Plano: `docs/plans/2026-10-01-app-android.md` · Spec: `docs/specs/2026-10-01-app-android-design.md`.
