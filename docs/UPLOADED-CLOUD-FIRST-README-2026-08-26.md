# Windows MSP AI Agent - Cloud First, Local Last

This package converts the Hardened v4 agent from local-first (Ollama only)
to **cloud first, local last**:

- Every chat / document / research / vision / embedding call tries your
  configured cloud API first.
- If that call fails for any reason (no key set, no network, timeout,
  HTTP error), it automatically falls back to your local Ollama instance -
  no manual intervention needed.
- Set `CLOUD_FIRST_MODE=false` in `.env` to force local-first (the
  original v4 behavior) without touching any code.

## Two ways to install

1. **Fresh install**: run `Fresh-MSP-Local-AI-Agent-Setup-Hardened-v4.ps1`
   in PowerShell as you would any other version of this installer. It now
   writes the cloud-first agent code (including the two new modules
   `cloud_llm.py` and `agent_client.py`) to disk.
2. **Existing install**: copy the contents of `windows_python_agent_from_v4/`
   over your existing agent folder (back up your `.env` and
   `data/brain/quick_answers.json` first if you've customized them).

## Configure your cloud provider

Edit `.env`:

```
CLOUD_API_BASE_URL=https://api.openai.com/v1
CLOUD_API_KEY=sk-...your key...
```

`CLOUD_API_BASE_URL` just needs to be an OpenAI-compatible
`/chat/completions` + `/embeddings` endpoint, so this also works unmodified
with Azure OpenAI, OpenRouter, Groq, Together, Fireworks, etc. - just swap
the base URL and key. No code changes required.

Per-role cloud model names (`CLOUD_MODEL_FAST`, `CLOUD_MODEL_DEEP`,
`CLOUD_MODEL_CODE`, `CLOUD_MODEL_DOC`, `CLOUD_MODEL_RESEARCH`,
`CLOUD_MODEL_VISION`, `CLOUD_EMBEDDING_MODEL`) default to reasonable OpenAI
model names - change them to match whatever provider you point at.

Local fallback models (`MODEL_FAST`, `MODEL_DEEP`, etc. and `OLLAMA_MODEL`)
are unchanged from the original v4 defaults.

## Fixed: local timeouts

The local Ollama client used to send `stream:false` and wait for one giant
response, so the whole reply had to be generated inside a single fixed
timeout window (180s). On modest hardware or bigger models that's easy to
blow through. It now uses Ollama's native streaming: tokens arrive
incrementally, and `REQUEST_TIMEOUT` (now 600s by default) only bounds the
gap between chunks, not the total reply time - so a slow multi-minute
generation no longer times out as long as it keeps making progress. A new
`OLLAMA_KEEP_ALIVE=30m` setting also keeps the model loaded in memory
between messages so you're not paying a reload cost on every chat turn.
If you were on the previous cloud-first build, just take the updated
`.env`, `llm.py`, `config.py`, and `agent_client.py`, or re-run the
installer.

## New CLI command

`/provider` - shows the current provider order (cloud-first vs local-first)
without a full `/status` call.

## One thing to know about the document index

Cloud and local embeddings are not numerically comparable. If you ever
change `CLOUD_EMBEDDING_MODEL`, `EMBEDDING_MODEL`, or flip
`CLOUD_FIRST_MODE`, run `/cleardocindex` then re-run `/ingestdoc` on your
files so the whole index was embedded with a single, consistent model.
