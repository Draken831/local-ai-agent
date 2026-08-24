# Local AI Agent

Cloud-first, local-fallback MSP-focused AI agent project optimized for response speed and resilience.

## Execution priority

The intended runtime order is:

1. **Cloud/API first** for the fastest normal responses and externally hosted reasoning/inference.
2. **Online research/web sources** when the task needs current information.
3. **Local quick-answer/cache/RAG paths** when they can answer immediately without a model call.
4. **Local Ollama last** as an offline/privacy/resilience fallback when cloud services are unavailable, blocked, too slow, or explicitly bypassed.

This is **not** intended to be a local-first inference architecture.

## Current baseline

This branch contains Android source/build deliverables and follows the same cloud-first, local-fallback routing strategy as `main`.

## Branches

- `main` — Windows/desktop source baseline
- `android-apk` — Android source/build/APK deliverables

## Security

Runtime state and sensitive material must not be committed, including `.env`, API keys, virtual environments, caches, logs, uploaded documents, local vector stores, PFX/private signing keys, generated secrets, and Android signing keystores.
