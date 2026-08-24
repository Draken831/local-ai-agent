from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

MODE_FILE = Path("data/runtime/mode.txt")
VALID_MODES = {"auto", "fast", "deep", "code", "doc", "research", "vision"}


@dataclass
class ModelRoute:
    task: str
    cloud_model: str
    local_model: str
    route: str
    reason: str


def set_mode(mode: str) -> str:
    mode = mode.lower().strip()
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode: {mode}")
    MODE_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODE_FILE.write_text(mode, encoding="utf-8")
    return mode


def get_mode() -> str:
    if not MODE_FILE.exists():
        return "auto"
    mode = MODE_FILE.read_text(encoding="utf-8").strip().lower()
    return mode if mode in VALID_MODES else "auto"


def _norm(text: str) -> str:
    text = str(text or "").lower()
    for a, b in {
        "defnder": "defender",
        "calender": "calendar",
        "exchnage": "exchange",
        "microsfot": "microsoft",
        "owershell": "powershell",
        "commnad": "command",
    }.items():
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s:._/-]", " ", text)).strip()


def _pair(settings, task: str) -> tuple[str, str]:
    cloud = {
        "fast": settings.cloud_model_fast,
        "deep": settings.cloud_model_deep,
        "code": settings.cloud_model_code,
        "doc": settings.cloud_model_doc,
        "research": settings.cloud_model_research,
        "vision": settings.cloud_model_vision,
    }[task]
    local = {
        "fast": settings.local_model_fast,
        "deep": settings.local_model_deep,
        "code": settings.local_model_code,
        "doc": settings.local_model_doc,
        "research": settings.local_model_research,
        "vision": settings.local_model_vision,
    }[task]

    if settings.cloud_model_force:
        cloud = settings.cloud_model_force
    if settings.local_model_force:
        local = settings.local_model_force
    return cloud, local


def choose_model(text: str, settings, context_type: str = "chat") -> ModelRoute:
    mode = get_mode()
    if mode != "auto":
        task = mode
        cloud, local = _pair(settings, task)
        return ModelRoute(task, cloud, local, f"mode-{task}", f"runtime mode {task}")

    if not settings.dynamic_model_routing:
        cloud, local = _pair(settings, "fast")
        return ModelRoute("fast", cloud, local, "default", "dynamic routing disabled")

    t = _norm(text)
    c = context_type.lower().strip()

    if c == "vision" or any(x in t for x in ["image", "screenshot", "picture"]):
        task, reason = "vision", "image task"
    elif c == "code" or any(x in t for x in ["powershell", "script", "ps1", "bash", "function", "compile", "automation"]):
        task, reason = "code", "code/script task"
    elif c == "document" or any(x in t for x in ["document", "pdf", "docx", "xlsx", "pptx", "ocr"]):
        task, reason = "doc", "document task"
    elif c == "research" or any(x in t for x in ["latest", "current", "vendor docs", "official docs", "cve", "release notes", "research"]):
        task, reason = "research", "research/current-information task"
    elif any(x in t for x in ["root cause", "deep", "analyze", "logs", "har", "architecture", "complex", "troubleshoot"]):
        task, reason = "deep", "deep reasoning task"
    else:
        task, reason = "fast", "default fast route"

    cloud, local = _pair(settings, task)
    return ModelRoute(task, cloud, local, task, reason)
