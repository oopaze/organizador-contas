#!/usr/bin/env bash
# Gera o APK de release assinado localmente (sem EAS).
#
# Requisitos desta maquina (Task 11 do plano):
#   - JDK 17 (JAVA_HOME)
#   - Android SDK em /opt/android-sdk com platform-tools, platforms;android-36,
#     build-tools;36.0.0, ndk;27.1.12297006 e cmake;3.22.1
#   - Keystore em /root/.poupix/poupix-release.jks
#     Senhas em mobile/.secrets/keystore.env (gitignored)
#
# Uso: ./scripts/build-apk.sh
# Saida: mobile/builds/poupix-<versao>.apk
set -euo pipefail

cd "$(dirname "$0")/.."

# --- Toolchain -----------------------------------------------------------------
if [[ -z "${JAVA_HOME:-}" ]] && command -v java >/dev/null 2>&1; then
  JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
  export JAVA_HOME
fi
export ANDROID_HOME="${ANDROID_HOME:-/opt/android-sdk}"
export PATH="$ANDROID_HOME/platform-tools:$PATH"

if [[ ! -x "$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager" ]]; then
  echo "Android SDK nao encontrado em $ANDROID_HOME (veja o README)" >&2
  exit 1
fi
if ! command -v java >/dev/null 2>&1; then
  echo "JDK nao encontrado (instale openjdk-17-jdk-headless)" >&2
  exit 1
fi

# --- Keystore ------------------------------------------------------------------
if [[ -f .secrets/keystore.env ]]; then
  # set -a exporta as variaveis do arquivo para o gradlew (System.getenv no Gradle)
  set -a
  # shellcheck disable=SC1091
  source .secrets/keystore.env
  set +a
fi
: "${POUPIX_STORE_PASSWORD:?defina POUPIX_STORE_PASSWORD em mobile/.secrets/keystore.env}"
: "${POUPIX_KEY_PASSWORD:?defina POUPIX_KEY_PASSWORD em mobile/.secrets/keystore.env}"
export POUPIX_KEYSTORE="${POUPIX_KEYSTORE:-/root/.poupix/poupix-release.jks}"
export POUPIX_KEY_ALIAS="${POUPIX_KEY_ALIAS:-poupix}"
if [[ ! -f "$POUPIX_KEYSTORE" ]]; then
  echo "Keystore nao encontrado em $POUPIX_KEYSTORE (veja o README)" >&2
  exit 1
fi

VERSION="$(node -p "require('./app.json').expo.version")"

# --- Projeto nativo ------------------------------------------------------------
# android/ e gerado (CNG) e ignorado no git; --clean garante build reprodutivel.
npx expo prebuild -p android --clean

# Assinatura de release no build.gradle gerado (nao versionado).
python3 - <<'PY'
import pathlib
import re

path = pathlib.Path('android/app/build.gradle')
text = path.read_text()

release_config = """
        release {
            storeFile file(System.getenv('POUPIX_KEYSTORE') ?: '/root/.poupix/poupix-release.jks')
            storePassword System.getenv('POUPIX_STORE_PASSWORD')
            keyAlias System.getenv('POUPIX_KEY_ALIAS') ?: 'poupix'
            keyPassword System.getenv('POUPIX_KEY_PASSWORD')
        }"""

if 'signingConfigs.release' in text:
    raise SystemExit('build.gradle ja tem signingConfigs.release; abortando')

# Primeiro troca a assinatura do bloco release (antes de inserir um "release {"
# novo em signingConfigs, que bagunçaria o match).
text, count = re.subn(
    r'(release\s*\{.*?)signingConfig signingConfigs\.debug',
    r'\1signingConfig signingConfigs.release',
    text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit('nao foi possivel trocar signingConfig signingConfigs.debug no bloco release')

if 'signingConfigs {' in text:
    text = text.replace('signingConfigs {', 'signingConfigs {' + release_config, 1)
else:
    text = text.replace('android {', 'android {\n    signingConfigs {' + release_config + '\n    }', 1)
path.write_text(text)
print('signingConfigs.release injetado em android/app/build.gradle')
PY

# --- Build ---------------------------------------------------------------------
# Maquina de 8 GB sem swap: 2 workers e heap do daemon do Kotlin limitado
# evitam OOM. Ajuste aqui se a maquina mudar.
# POUPIX_ARCHS limita as ABIs (ex.: "arm64-v8a"); vazio usa o default do template.
GRADLE_ARCH_ARGS=()
if [[ -n "${POUPIX_ARCHS:-}" ]]; then
  GRADLE_ARCH_ARGS+=("-PreactNativeArchitectures=${POUPIX_ARCHS}")
fi

./android/gradlew -p android assembleRelease --no-daemon \
  "${GRADLE_ARCH_ARGS[@]}" \
  -Dorg.gradle.jvmargs="-Xmx2048m -XX:MaxMetaspaceSize=512m" \
  -Dorg.gradle.workers.max=2 \
  -Dkotlin.daemon.jvmargs="-Xmx1024m"

# --- Artefato ------------------------------------------------------------------
mkdir -p builds
cp android/app/build/outputs/apk/release/app-release.apk "builds/poupix-${VERSION}.apk"
echo "APK: mobile/builds/poupix-${VERSION}.apk ($(du -h "builds/poupix-${VERSION}.apk" | cut -f1))"
