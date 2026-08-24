# Local AI Agent

Local-first MSP-focused AI agent project built around Ollama, dynamic model routing, local SearXNG research, document parsing/OCR, local RAG, quick learned answers, and PowerShell/Linux automation support.

## Current baseline

This repository is being published from the Hardened v4 project baseline.

Key capabilities:
- Ollama local LLM backend
- Dynamic routing for fast, deep, code, document, research, and vision workloads
- CLI and Tkinter GUI
- Local SearXNG web research
- URL fetch support with private/internal policy controls
- PDF/DOCX/XLSX/PPTX/image parsing and OCR
- Local document indexing/RAG using Ollama embeddings
- Quick-answer/learning system
- MSP-focused knowledge and script-generation standards
- PowerShell code-signing helpers

## Branches

- `main` — Windows/local-agent source baseline
- `android-apk` — Android/APK deliverables

## Security

Runtime state and sensitive/local-only material must not be committed, including `.env`, virtual environments, caches, logs, uploaded documents, local vector stores, PFX/private signing keys, and generated secrets.
