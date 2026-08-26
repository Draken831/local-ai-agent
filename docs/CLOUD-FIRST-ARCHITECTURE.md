# Cloud-First Architecture

## Strict request order

```text
normal request
  -> task/model route
  -> cloud provider
       research route -> cloud web search tool (when enabled)
       success -> response
       failure/timeout/rate-limit -> circuit breaker
  -> local fallback layer
       local quick/cache/RAG or SearXNG when explicitly requested/needed
       Ollama fallback
  -> response or final provider error
```

Local quick answers and local SearXNG are **not** automatically executed before cloud on the normal request path.

## Speed controls

- 3-second default cloud connect timeout
- 15-second default cloud read timeout
- zero automatic retries by default
- circuit breaker after repeated failures
- immediate local fallback while the cloud circuit is open

## Runtime policy

The authoritative machine-readable policy is `data/brain/runtime-policy.json`. `LOCAL_SEARXNG_PRECONTEXT=false` is the current setting name; legacy `ONLINE_FIRST_MODE` is read only for backward compatibility.

## Backward compatibility

The loader still understands Hardened v4 names such as `MODEL_FAST`, `MODEL_DEEP`, `MODEL_CODE`, `MODEL_DOC`, `MODEL_RESEARCH`, `VISION_MODEL`, `EMBEDDING_MODEL`, `OLLAMA_MODEL`, `REQUEST_TIMEOUT`, and `MAX_RESPONSE_TOKENS`. Those values are treated as local fallback settings.

## Security

`.env` remains excluded from source control. API keys are loaded from environment variables or `.env` and are never stored in the repository.

## Interface architecture

The GUI is the normal application interface. `msp_agent.launcher` starts the GUI unless `--cli` is explicitly supplied.

```text
run.ps1 / msp-agent / Desktop shortcut
          |
          v
    msp_agent.launcher
          |
          +--> GUI (default)
          |
          +--> CLI only with --cli
```

The GUI invokes the same cloud-first `AIClient` gateway as the CLI; it is not a separate agent process.
