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

## Backward compatibility

The loader still understands Hardened v4 names such as `MODEL_FAST`, `MODEL_DEEP`, `MODEL_CODE`,
`MODEL_DOC`, `MODEL_RESEARCH`, `VISION_MODEL`, `EMBEDDING_MODEL`, `OLLAMA_MODEL`,
`REQUEST_TIMEOUT`, and `MAX_RESPONSE_TOKENS`. Those values are treated as local fallback settings.

## Security

`.env` remains excluded from source control. API keys are loaded from environment variables or `.env`
and are never stored in the repository.
