# Cloud-First Architecture

## Request path

```text
request
  -> quick-answer check
  -> task/model route
  -> cloud provider
       success -> response
       timeout/network/429/5xx/config failure -> failure counter
       repeated failures -> temporary cloud circuit open
  -> local Ollama fallback
  -> response or final provider error
```

The cloud path uses a short connect timeout, bounded read timeout, one retry by default, and a circuit breaker. Repeated cloud failures therefore do not make every request wait for a dead provider.

The settings loader understands both the new `CLOUD_*`/`LOCAL_*` names and the earlier Hardened v4 `MODEL_*`, `VISION_MODEL`, `EMBEDDING_MODEL`, `OLLAMA_MODEL`, `REQUEST_TIMEOUT`, and `MAX_RESPONSE_TOKENS` names. Existing v4 values become local fallback values.

`.env` is excluded from source control. API keys are read from environment variables or `.env` only.
