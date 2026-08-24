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

This repository is being published from the Hardened v4 project baseline, but its routing layer is being adapted from the earlier local-first implementation to the cloud-first priority above.

Key capabilities:
- Cloud/API primary inference path
- Local Ollama fallback backend
- Dynamic routing for fast, deep, code, document, research, and vision workloads
- CLI and GUI
- Web research support
- URL fetch support with private/internal policy controls
- PDF/DOCX/XLSX/PPTX/image parsing and OCR
- Document indexing/RAG
- Quick-answer/learning system
- MSP-focused knowledge and script-generation standards
- PowerShell code-signing helpers

## Branches

- `main` — Windows/desktop source baseline
- `android-apk` — Android source/build/APK deliverables

## Security

Runtime state and sensitive material must not be committed, including `.env`, API keys, virtual environments, caches, logs, uploaded documents, local vector stores, PFX/private signing keys, and generated secrets.
