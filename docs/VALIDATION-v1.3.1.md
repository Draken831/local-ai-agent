# Validation — v1.3.1

Consistency patch after full active-tree audit.

## Required invariants

- Version: 1.3.1
- Default interface: GUI
- Provider priority: `cloud,local`
- Cloud connect/read timeout: 3s / 15s
- Automatic cloud retries: 0
- Local Ollama: fallback or explicit only
- Local SearXNG pre-context: disabled by default
- Quick answers: explicit local path
- Active metadata contains no `local-first` operating model
- Active installer directory contains current installer only
- Historical/superseded material is isolated under `legacy/`
- Live `.env` / API keys: not committed
