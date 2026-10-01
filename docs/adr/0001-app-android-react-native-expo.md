# 0001. App Android nativo com React Native/Expo

Status: Aceito
Tipo: Técnica
Data: 2026-10-01

## Contexto e Problema

O Poupix hoje é um PWA instalável (spec de 2026-09-09). O dono do produto quer um app Android nativo, instalável por APK direto no aparelho, com UX nativa e leitura offline — e pediu que o app siga as telas do PWA existente. Na decisão do PWA, o React Native foi descartado porque o objetivo era apenas "instalável no celular". O objetivo mudou, então a decisão é revisitada.

## Motivação / Drivers

- UX nativa (gestos, teclado, navegação) e leitura offline no Android
- Distribuição por APK direto, sem loja nesta fase
- Reaproveitar a lógica existente (services/tipos) sem tocar no backend
- Viabilizar build do APK na máquina de desenvolvimento atual

## Opções Consideradas

- Manter o PWA atual
- Capacitor (empacotar o web existente em shell nativo)
- React Native/Expo (managed)

## Decisão

Escolhemos **React Native com Expo (managed)**, em um projeto novo `mobile/` com Expo Router e NativeWind, porque entrega UX nativa de verdade com o menor atrito de tooling, e porque a camada de serviços do PWA porta quase 1:1, mantendo o backend intacto.

## Prós e Contras das Opções

### Manter o PWA

+ Zero trabalho novo; já instalável; uma base de código só
- Continua UX de web em shell; offline limitado à casca; não atende ao objetivo de app nativo

### Capacitor

+ Dias para ter app instalável; reaproveita 100% da UI web; uma base de código só
- Continua sendo WebView, não UX nativa; risco de rejeição de loja (guideline 4.2) se publicar; capacidades nativas dependem de plugins

### React Native/Expo

+ UX nativa real; ecossistema cobre auth storage, seleção de arquivos e share; services e tipos portam; build de APK viável
- Segunda base de código (web + mobile); UI reescrita (Radix/Tailwind/DOM não existem no RN); sem emulador na máquina de build

## Consequências

- **Positivas:** app nativo Android com leitura offline; caminho aberto para push, câmera e loja; o web permanece no ar para compartilhamento de ator, OAuth do MCP e desktop.
- **Negativas:** duas bases (web + mobile) passam a coexistir e exigem disciplina de paridade; duas toolchains para manter.
- **Riscos / Mitigações:** divergência de features entre as bases — manter `services/` idêntico e mudanças de contrato no backend; build local pesado — fallback para EAS Build.

## Links

- Spec do app Android: docs/specs/2026-10-01-app-android-design.md
- Spec do PWA: docs/superpowers/specs/2026-09-09-poupix-pwa-design.md
