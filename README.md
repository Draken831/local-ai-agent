# MSP AI Agent — Android Cloud First

This branch contains the full native Android source for **v1.3.0**.

Provider priority is **cloud first -> local fallback**. Normal chat no longer invokes Local Quick before cloud; Local Quick is an explicit UI action. Local SearXNG pre-context is disabled by default. Cloud chat and vision use a 15-second timeout so failed cloud calls fall back promptly.

Source lives under `android/`.

A compiled APK is not included because the current build environment does not contain the Android SDK/build tools. Build with Android Studio or `android/build-apk.ps1` on a machine with the Android SDK and compatible Gradle tooling.
