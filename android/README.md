# MSP AI Agent - Android Cloud First

Native Android companion/client for the MSP AI Agent v1.3.0 cloud-first baseline.

## Provider order: cloud first, local last
Chat, document, research and vision requests are sent to a configured OpenAI-compatible cloud API first. If that call fails (no key, no network, timeout, error), the app automatically retries against your local Ollama host. Set both under Connection & Model Settings; toggle "Cloud-first" off to force local-only.

## Implemented
- Native Android launcher and UI, no WebView shell.
- Cloud-first chat via any OpenAI-compatible `/chat/completions` endpoint, with automatic local Ollama fallback via `/api/chat`.
- Dynamic model routing: fast, deep, code, document, research and vision.
- Optional SearXNG JSON research context for latest/current/research prompts; disabled by default so normal research remains cloud-first.
- Bundled local quick-answer seed data, invoked explicitly through **Local Quick** so normal chat remains cloud-first.
- Editable local knowledge store.
- Text/script/log document analysis through Android Storage Access Framework.
- Image/screenshot analysis using the configured cloud vision model, falling back to the local Ollama vision model.
- Native Android system controls including user-approved WRITE_SETTINGS, brightness, screen timeout, settings panels, Device Admin lock, Device Owner detection, and allow-listed optional root checks/actions.

## Architecture constraint
Cloud chat/vision requests use a 15-second timeout so a failed cloud endpoint falls back to local promptly. Local Ollama models are not embedded in the APK; configure a reachable LAN/VPN Ollama host. Local SearXNG is optional and disabled as a pre-cloud context source by default.

## Build
- compileSdk 36
- targetSdk 36
- minSdk 29
- Android Gradle Plugin 9.3.0
- Java 17

Open this folder in Android Studio and build `app` as an APK, or use `build-apk.ps1` when the Android SDK/Gradle are installed.

## Version
- source version: 1.3.0
- versionCode: 2
- provider priority: cloud -> local fallback
- local quick answers: explicit only
- local SearXNG pre-context: disabled by default
