from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from dotenv import dotenv_values
import os


def _get(env, key: str, default: str = "") -> str:
    value = os.getenv(key)
    if value is not None and str(value).strip():
        return str(value).strip().strip('"').strip("'")
    return str(env.get(key, default)).strip().strip('"').strip("'")


def _bool(env, key: str, default: bool = False) -> bool:
    return _get(env, key, str(default)).lower() in {"1", "true", "yes", "y", "on"}


def _int(env, key: str, default: int) -> int:
    try:
        return int(_get(env, key, str(default)))
    except Exception:
        return default


def _order(env) -> tuple[str, ...]:
    raw = _get(env, "AI_PROVIDER_ORDER", "cloud,local")
    values = tuple(x.strip().lower() for x in raw.split(",") if x.strip())
    valid = tuple(x for x in values if x in {"cloud", "local"})
    return valid or ("cloud", "local")


@dataclass
class Settings:
    root: Path

    ai_provider_order: tuple[str, ...]
    cloud_ai_enabled: bool
    cloud_api_style: str
    cloud_api_base_url: str
    cloud_api_key: str
    cloud_timeout_connect: int
    cloud_timeout_read: int
    cloud_retries: int
    cloud_circuit_breaker_failures: int
    cloud_circuit_breaker_seconds: int
    cloud_max_response_tokens: int
    cloud_web_search_enabled: bool
    cloud_model_fast: str
    cloud_model_deep: str
    cloud_model_code: str
    cloud_model_doc: str
    cloud_model_research: str
    cloud_model_vision: str
    cloud_model_force: str
    cloud_embeddings_enabled: bool
    cloud_embedding_model: str

    local_fallback_enabled: bool
    ollama_base_url: str
    local_request_timeout: int
    local_model_fast: str
    local_model_deep: str
    local_model_code: str
    local_model_doc: str
    local_model_research: str
    local_model_vision: str
    local_model_force: str
    local_embedding_model: str

    dynamic_model_routing: bool
    dynamic_model_announce: bool

    searxng_base_url: str
    online_first_mode: bool
    online_research_max_results: int
    online_research_fetch_top: int
    allow_private_urls: bool

    document_max_chars: int
    document_context_chars: int
    document_cache_enabled: bool
    tesseract_cmd: str
    default_output_path: str
    script_log_path: str
    allow_destructive_actions: bool
    require_confirmation_for_high_risk: bool

    # Backward compatibility with v4 modules.
    @property
    def request_timeout(self) -> int:
        return self.local_request_timeout

    @property
    def max_response_tokens(self) -> int:
        return self.cloud_max_response_tokens

    @property
    def ollama_model(self) -> str:
        return self.local_model_fast

    @property
    def model_fast(self) -> str:
        return self.local_model_fast

    @property
    def model_deep(self) -> str:
        return self.local_model_deep

    @property
    def model_code(self) -> str:
        return self.local_model_code

    @property
    def model_doc(self) -> str:
        return self.local_model_doc

    @property
    def model_research(self) -> str:
        return self.local_model_research

    @property
    def model_force(self) -> str:
        return self.local_model_force

    @property
    def vision_model(self) -> str:
        return self.local_model_vision

    @property
    def embedding_model(self) -> str:
        return self.local_embedding_model


def load_settings(root: Path | None = None) -> Settings:
    root = (root or Path.cwd()).resolve()
    env = dotenv_values(root / ".env") if (root / ".env").exists() else {}

    old_fast = _get(env, "MODEL_FAST", _get(env, "OLLAMA_MODEL", "llama3.2:3b"))
    old_deep = _get(env, "MODEL_DEEP", "qwen2.5:7b")
    old_code = _get(env, "MODEL_CODE", "qwen2.5-coder:7b")
    old_doc = _get(env, "MODEL_DOC", old_fast)
    old_research = _get(env, "MODEL_RESEARCH", old_fast)
    old_force = _get(env, "MODEL_FORCE", "")
    old_vision = _get(env, "VISION_MODEL", "llama3.2-vision")
    old_embedding = _get(env, "EMBEDDING_MODEL", "nomic-embed-text")

    return Settings(
        root=root,
        ai_provider_order=_order(env),
        cloud_ai_enabled=_bool(env, "CLOUD_AI_ENABLED", _bool(env, "CLOUD_FIRST_MODE", True)),
        cloud_api_style=_get(env, "CLOUD_API_STYLE", "responses").lower(),
        cloud_api_base_url=_get(env, "CLOUD_API_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        cloud_api_key=_get(env, "CLOUD_API_KEY", _get(env, "OPENAI_API_KEY", "")),
        cloud_timeout_connect=_int(env, "CLOUD_TIMEOUT_CONNECT", 3),
        cloud_timeout_read=_int(env, "CLOUD_TIMEOUT_READ", 15),
        cloud_retries=_int(env, "CLOUD_RETRIES", 0),
        cloud_circuit_breaker_failures=_int(env, "CLOUD_CIRCUIT_BREAKER_FAILURES", 2),
        cloud_circuit_breaker_seconds=_int(env, "CLOUD_CIRCUIT_BREAKER_SECONDS", 30),
        cloud_max_response_tokens=_int(env, "CLOUD_MAX_RESPONSE_TOKENS", _int(env, "MAX_RESPONSE_TOKENS", 900)),
        cloud_web_search_enabled=_bool(env, "CLOUD_WEB_SEARCH_ENABLED", True),
        cloud_model_fast=_get(env, "CLOUD_MODEL_FAST", "gpt-5.6-luna"),
        cloud_model_deep=_get(env, "CLOUD_MODEL_DEEP", "gpt-5.6-terra"),
        cloud_model_code=_get(env, "CLOUD_MODEL_CODE", "gpt-5.6-terra"),
        cloud_model_doc=_get(env, "CLOUD_MODEL_DOC", "gpt-5.6-luna"),
        cloud_model_research=_get(env, "CLOUD_MODEL_RESEARCH", "gpt-5.6-luna"),
        cloud_model_vision=_get(env, "CLOUD_MODEL_VISION", "gpt-5.6-luna"),
        cloud_model_force=_get(env, "CLOUD_MODEL_FORCE", ""),
        cloud_embeddings_enabled=_bool(env, "CLOUD_EMBEDDINGS_ENABLED", True),
        cloud_embedding_model=_get(env, "CLOUD_EMBEDDING_MODEL", "text-embedding-3-small"),

        local_fallback_enabled=_bool(env, "LOCAL_FALLBACK_ENABLED", _bool(env, "FALLBACK_TO_LOCAL", True)),
        ollama_base_url=_get(env, "OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/"),
        local_request_timeout=_int(env, "LOCAL_REQUEST_TIMEOUT", _int(env, "REQUEST_TIMEOUT", 180)),
        local_model_fast=_get(env, "LOCAL_MODEL_FAST", old_fast),
        local_model_deep=_get(env, "LOCAL_MODEL_DEEP", old_deep),
        local_model_code=_get(env, "LOCAL_MODEL_CODE", old_code),
        local_model_doc=_get(env, "LOCAL_MODEL_DOC", old_doc),
        local_model_research=_get(env, "LOCAL_MODEL_RESEARCH", old_research),
        local_model_vision=_get(env, "LOCAL_MODEL_VISION", old_vision),
        local_model_force=_get(env, "LOCAL_MODEL_FORCE", old_force),
        local_embedding_model=_get(env, "LOCAL_EMBEDDING_MODEL", old_embedding),

        dynamic_model_routing=_bool(env, "DYNAMIC_MODEL_ROUTING", True),
        dynamic_model_announce=_bool(env, "DYNAMIC_MODEL_ANNOUNCE", True),

        searxng_base_url=_get(env, "SEARXNG_BASE_URL", ""),
        online_first_mode=_bool(env, "LOCAL_SEARXNG_PRECONTEXT", _bool(env, "ONLINE_FIRST_MODE", False)),
        online_research_max_results=_int(env, "ONLINE_RESEARCH_MAX_RESULTS", 5),
        online_research_fetch_top=_int(env, "ONLINE_RESEARCH_FETCH_TOP", 3),
        allow_private_urls=_bool(env, "ALLOW_PRIVATE_URLS", False),

        document_max_chars=_int(env, "DOCUMENT_MAX_CHARS", 16000),
        document_context_chars=_int(env, "DOCUMENT_CONTEXT_CHARS", 7000),
        document_cache_enabled=_bool(env, "DOCUMENT_CACHE_ENABLED", True),
        tesseract_cmd=_get(env, "TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
        default_output_path=_get(env, "DEFAULT_OUTPUT_PATH", r"C:\NSU"),
        script_log_path=_get(env, "SCRIPT_LOG_PATH", r"C:\NSU"),
        allow_destructive_actions=_bool(env, "ALLOW_DESTRUCTIVE_ACTIONS", False),
        require_confirmation_for_high_risk=_bool(env, "REQUIRE_CONFIRMATION_FOR_HIGH_RISK", True),
    )
