# MSP AI Agent - Android Cloud First

Native Android companion/client for the MSP AI Agent v1.3.1 cloud-first baseline.

## Provider order: cloud first, local last
Chat, document, research and vision requests are sent to a configured
OpenAI-compatible cloud API first. If that call fails (no key, no network,
timeout, error), the app automatically retries against your local Ollama
host. Set both under Connection & Model Settings. Cloud-first is the default; local-only is an explicit diagnostic/offline override. The Windows baseline uses the equivalent `AI_PROVIDER_ORDER=cloud,local` policy.

## Implemented
- Native Android launcher and UI, no WebView shell.
- Cloud-first chat via any OpenAI-compatible `/chat/completions` endpoint, with automatic local Ollama fallback via `/api/chat`.
- Dynamic model routing: fast, deep, code, document, research and vision (each role has its own cloud model and local fallback model).
- Optional SearXNG JSON research context for latest/current/research prompts; disabled by default so normal research remains cloud-first.
- Bundled local quick-answer seed data, invoked explicitly through **Local Quick** so normal chat remains cloud-first.
- Editable local knowledge store.
- Text/script/log document analysis through Android Storage Access Framework.
- Image/screenshot analysis using the configured cloud vision model, falling back to the local Ollama vision model.
- Native Android system controls:
  - User-approved `WRITE_SETTINGS` path.
  - Brightness control.
  - Screen timeout control.
  - Wi-Fi / Internet / notification settings panels.
  - Device Admin activation and local `Lock Now`.
  - Device Owner status detection for Android Enterprise expansion.
  - Optional root detection with an explicit, fixed allow-list of benign system actions; no arbitrary root shell.

## Architecture constraint
Cloud calls need only a reachable internet connection and a valid API key. Cloud chat/vision requests use a 15-second timeout so a failed cloud endpoint falls back to local promptly. For the local-fallback path, Ollama desktop/server models are not embedded in this APK: set `Ollama base URL` to a reachable Windows/Linux system running the current Windows agent's Ollama service. If the phone is on the same LAN, do not use `127.0.0.1`; use the host's LAN/VPN address and allow TCP 11434 only from trusted networks. Set SearXNG similarly (typically TCP 8080).

## Android system-control model
A normal third-party APK cannot write `Settings.Secure` freely. Deeper supported management should use Device Owner / Android Enterprise. Root actions are enabled only when `su` already exists and are intentionally allow-listed.

## Build
Current project values:
- compileSdk 36
- targetSdk 36
- minSdk 29
- Android Gradle Plugin 9.3.0
- Java 17

Open this folder in Android Studio and build `app` as an APK. A debug APK is automatically debug-signed. For production/internal MSP deployment, configure your own release signing key and protect it outside the repository.

## Device Owner
Device Owner provisioning is a deployment decision, not a normal in-app permission prompt. It is intended for dedicated/fully managed devices and typically requires provisioning during device setup. The app currently detects Device Owner status and provides the framework for extending managed controls.

## Security design
- Cloud API keys are encrypted with an Android Keystore-backed AES key; plaintext API keys are not retained in normal SharedPreferences.
- Cloud API base URLs must use HTTPS before a key is sent.
- Android backup is disabled for the app configuration.
- Destructive Android actions are not exposed.
- No arbitrary `su` command text box.
- Privileged root actions require a local tap and confirmation.
- The app does not attempt to grant itself signature-only permissions such as `WRITE_SECURE_SETTINGS`.

## Version

- source version: 1.3.1
- versionCode: 3
- provider priority: cloud -> local fallback
- local quick answers: explicit only
- local SearXNG pre-context: disabled by default
