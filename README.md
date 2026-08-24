# Local AI Agent — Cloud First / Local Fallback

This repository contains the corrected runtime architecture for the MSP AI Agent.

## Runtime priority

1. **Cloud inference first** for normal chat, code, document, research and vision tasks.
2. **Cloud embeddings first** when enabled.
3. **Online research** when current information is required.
4. **Local quick answers/cache/RAG** where they can answer immediately.
5. **Ollama local models last** as fallback when cloud is unavailable, times out, is rate-limited, or is explicitly disabled.

The earlier Hardened v4 implementation instantiated `OllamaClient` directly from the CLI, GUI, router and document indexer. v1.1 replaces that coupling with a provider gateway.

## Speed behavior

Cloud calls use a short connect timeout, bounded read timeout, one retry by default, and a circuit breaker. Repeated cloud failures do not force every request to wait for a dead provider; the agent temporarily opens the cloud circuit and immediately uses the local fallback.

## Setup

```powershell
Copy-Item .env.example .env
notepad .env
# Set CLOUD_API_KEY
.\scripts\setup.ps1
.\scripts\run.ps1
```

Never commit `.env` or API keys.

## Existing Hardened v4 installation

Run the migration script from this corrected repository/package:

```powershell
.\scripts\migrate-v4-to-cloud-first.ps1 -TargetRoot "C:\Projects\msp-local-ai-agent-fresh"
```

The migration backs up and replaces only the provider/routing files and preserves learned answers, uploaded documents, caches, knowledge and MSP data.

## Defaults

- Fast/document/research/vision cloud model: `gpt-5.6-luna`
- Deep/code cloud model: `gpt-5.6-terra`
- Local fast: `llama3.2:3b`
- Local deep: `qwen2.5:7b`
- Local code: `qwen2.5-coder:7b`
- Local vision: `llama3.2-vision`

All model names are configurable in `.env`.

## Branches

- `main` — desktop/source baseline
- `android-apk` — Android source/build/APK deliverables
