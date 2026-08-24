# MSP AI Agent — Cloud First / GUI Default

This is the corrected **v1.2.0** runtime architecture for the MSP AI Agent.

## Strict runtime priority

1. **Cloud inference first** for normal chat, code, document, research and vision tasks.
2. **Cloud-native web search first** for current-information/research routes when enabled.
3. **Cloud embeddings first** for document indexing/RAG when enabled.
4. **Local SearXNG, quick answers, cache/RAG and Ollama only as explicit or fallback paths.**

The earlier Hardened v4 implementation instantiated `OllamaClient` directly and could run local quick/search paths before cloud. v1.2.0 replaces that coupling with a provider gateway and keeps the normal request path cloud-first end-to-end.

## Speed / failover behavior

Defaults are intentionally aggressive:

- cloud connect timeout: 3 seconds;
- cloud read timeout: 15 seconds;
- automatic cloud retries: 0;
- circuit breaker opens after 2 consecutive cloud failures;
- circuit remains open for 30 seconds;
- while open, requests skip the failing cloud endpoint and go directly to local fallback.

All values are configurable in `.env`.

## Default interface

The agent now launches the **GUI by default**. You do not start the CLI and GUI separately.

- `msp-agent` -> GUI
- `.\scripts\run.ps1` -> GUI
- `Start-MSP-AI-Agent.cmd` -> GUI
- Desktop shortcut created by setup -> GUI
- `msp-agent --cli` or `.\scripts\run-cli.ps1` -> explicit diagnostic/admin CLI

The GUI includes chat, route selection, provider status, document attachment, image attachment, explicit local quick answers, and explicit local SearXNG search.

## First setup

```powershell
Copy-Item .env.example .env
notepad .env
# Set CLOUD_API_KEY
.\scripts\setup.ps1
.\scripts\healthcheck.ps1
.\scripts\run.ps1
```

Never commit `.env` or API keys.

## Upgrade an existing Hardened v4 project

From this corrected package/repository:

```powershell
.\scripts\migrate-v4-to-cloud-first.ps1 -TargetRoot "C:\Projects\msp-local-ai-agent-fresh"
```

The migration backs up the files it replaces and preserves learned answers, uploaded documents, caches, knowledge and MSP data.

## Single-script installer / updater

```powershell
.\installers\Install-MSP-AI-Agent-CloudFirst-v1.2.0.ps1
```

Use `-InstallPrereqs` if Python is missing. Use `-InstallLocalFallback` if you also want Ollama installed as the fallback provider.

## Default model routing

- Cloud fast/document/research/vision: `gpt-5.6-luna`
- Cloud deep/code: `gpt-5.6-terra`
- Local fast: `llama3.2:3b`
- Local deep: `qwen2.5:7b`
- Local code: `qwen2.5-coder:7b`
- Local vision: `llama3.2-vision`

All model names are configurable in `.env`.

## Explicit local commands

- `/quick <query>` — local quick-answer database
- `/search <query>` — local SearXNG research path
- `/models` / `/pull <model>` — local Ollama management

These commands are explicit; they are not inserted ahead of cloud on normal requests.

## Quick-answer knowledge

The package includes **97 curated quick-answer rules** in `data/brain/quick_answers.bundle/`, with typo-tolerant/natural-variation matching and human-editable local override support. See `docs/QUICK-ANSWERS.md`.
