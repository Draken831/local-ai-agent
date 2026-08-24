# Local AI Agent — Android Branch

This branch is reserved for Android source/build/APK deliverables and follows the same **v1.1.1 strict cloud-first / local-fallback** provider contract as `main`.

## Runtime priority

1. Cloud inference first.
2. Cloud-native web search for research/current-information routes when supported.
3. Local/on-device or LAN services only as explicit or fallback paths.
4. Ollama/local model inference last.

The Android implementation must not execute local quick-answer, local search, or local model paths ahead of a healthy configured cloud provider.

## Speed / failover contract

- short cloud connect/read timeouts;
- zero automatic cloud retries by default;
- circuit breaker after repeated cloud failures;
- local fallback only after cloud is unavailable, fails, times out, or is explicitly bypassed.

## Security

No cloud API key may be committed to GitHub or embedded as a plaintext constant in an APK. Android credentials must be supplied at runtime and stored using Android secure storage mechanisms.

## Build status

The provider architecture is corrected and documented. A real compiled APK is **not yet present on this branch** because the prior generation environment did not have the Android SDK/build tools required to compile it.

- `main` — corrected desktop/runtime source v1.1.1
- `android-apk` — Android source/build/APK deliverables
