from __future__ import annotations
from .llm import OllamaClient
from .cloud_llm import CloudClient

class HybridClient:
    """Cloud-first, local-last model client.

    Every call tries the configured cloud provider first (when
    settings.cloud_first_mode is on and a CLOUD_API_KEY is set). If that
    call raises (missing key, no network, timeout, HTTP error) and
    settings.fallback_to_local is true, the same call is retried against
    the local Ollama instance so the agent keeps working offline or when
    the cloud provider is unavailable.

    Set CLOUD_FIRST_MODE=false in .env to force local-first behavior
    (the original v4 default) without touching call sites.
    """
    def __init__(self, settings, cloud_model, local_model):
        self.settings=settings
        self.cloud_model=cloud_model
        self.local_model=local_model
        self.cloud=CloudClient(settings.cloud_api_base_url, settings.cloud_api_key, cloud_model, settings.cloud_timeout, settings.max_response_tokens) if settings.cloud_api_key else None
        self.local=OllamaClient(settings.ollama_base_url, local_model, settings.request_timeout, settings.max_response_tokens, settings.ollama_keep_alive)
        self.model=cloud_model if self._cloud_active() else local_model
        self.last_used="cloud" if self._cloud_active() else "local"

    def _cloud_active(self):
        return bool(self.cloud) and self.settings.cloud_first_mode

    def _try_cloud_then_local(self, cloud_fn, local_fn):
        if self._cloud_active():
            try:
                out=cloud_fn(); self.last_used="cloud"; return out
            except Exception as e:
                if not self.settings.fallback_to_local: raise
                self.last_used="local (cloud failed: %s)" % e
        else:
            self.last_used="local"
        return local_fn()

    def chat(self, messages, model=None, temperature=0.2):
        return self._try_cloud_then_local(
            lambda: self.cloud.chat(messages, model or self.cloud_model, temperature),
            lambda: self.local.chat(messages, model or self.local_model, temperature),
        )

    def vision(self, image_path, prompt, model=None):
        return self._try_cloud_then_local(
            lambda: self.cloud.vision(image_path, prompt, model or self.cloud_model),
            lambda: self.local.vision(image_path, prompt, model or self.local_model),
        )

    def embed(self, text, model=None):
        return self._try_cloud_then_local(
            lambda: self.cloud.embed(text, model or self.cloud_model),
            lambda: self.local.embed(text, model or self.local_model),
        )

    def health(self):
        if self._cloud_active():
            ok,msg=self.cloud.health()
            if ok: return True, f"cloud reachable ({self.cloud_model}) - {msg}"
            if not self.settings.fallback_to_local: return False, msg
        ok,msg=self.local.health()
        return ok, f"local ({self.local_model}) - {msg}"

    def list_models(self):
        if self._cloud_active():
            try: return self.cloud.list_models()
            except Exception: pass
        return self.local.list_models()

    def pull_model(self, model):
        if self._cloud_active():
            return self.cloud.pull_model(model)
        return self.local.pull_model(model)
