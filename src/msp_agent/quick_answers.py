from __future__ import annotations

import json
import re
from pathlib import Path


_TYPO_MAP = {
    "defnder": "defender",
    "defendr": "defender",
    "calender": "calendar",
    "exchnage": "exchange",
    "microsfot": "microsoft",
    "powershel": "powershell",
    "owershell": "powershell",
    "commnad": "command",
    "compuer": "computer",
    "computuer": "computer",
    "gpoo": "gpo",
    "updats": "updates",
    "windwos": "windows",
    "outlok": "outlook",
    "fortigat": "fortigate",
    "searx": "searxng",
}


def norm(text):
    text = str(text or "").lower()
    for bad, good in _TYPO_MAP.items():
        text = text.replace(bad, good)
    text = re.sub(r"[^a-z0-9\s:._/\\-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _stem(token: str) -> str:
    if len(token) > 5 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 5 and token.endswith("es"):
        return token[:-2]
    if len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def _tokens(text: str) -> set[str]:
    return {_stem(x) for x in norm(text).split() if x}


def path():
    return Path.cwd() / "data" / "brain" / "quick_answers.json"


def modular_path():
    return Path.cwd() / "data" / "brain" / "quick_answers"


def bundle_path():
    return Path.cwd() / "data" / "brain" / "quick_answers.json.gz"


def _load_json_file(file_path: Path) -> list[dict]:
    try:
        data = json.loads(file_path.read_text(encoding="utf-8-sig"))
    except Exception:
        return []
    return [x for x in data if isinstance(x, dict)] if isinstance(data, list) else []


def load_answers():
    items = []

    # Bundled curated database.
    bundle = bundle_path()
    if bundle.exists():
        try:
            import gzip
            data = json.loads(gzip.decompress(bundle.read_bytes()).decode("utf-8"))
            if isinstance(data, list):
                items.extend(x for x in data if isinstance(x, dict))
        except Exception:
            pass

    # Legacy/local override file remains human-editable.
    legacy = path()
    if legacy.exists():
        items.extend(_load_json_file(legacy))

    # Optional modular override directory is also supported.
    folder = modular_path()
    if folder.exists():
        for file_path in sorted(folder.glob("*.json")):
            items.extend(_load_json_file(file_path))

    # Last ID wins, so local JSON files can override bundled entries by ID.
    deduped = {}
    for item in items:
        item_id = str(item.get("id", "")).strip()
        if item_id:
            deduped[item_id] = item
    return list(deduped.values())


def save_answers(items):
    # Compatibility writer: callers that explicitly save still target the legacy file.
    path().parent.mkdir(parents=True, exist_ok=True)
    path().write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def _term_match(text: str, term: str) -> bool:
    nt = norm(text)
    nq = norm(term)
    if not nq:
        return False
    if nq in nt:
        return True

    wanted = _tokens(nq)
    actual = _tokens(nt)
    if not wanted:
        return False

    if len(wanted) == 1:
        return wanted.issubset(actual)

    return wanted.issubset(actual)


def _contains_any(text, terms):
    return any(_term_match(text, x) for x in terms)


def _matches(item, text):
    if _contains_any(text, item.get("exclude_any") or []):
        return False

    any_terms = item.get("match_any") or []
    if any_terms and not _contains_any(text, any_terms):
        return False

    for term in item.get("match_all") or []:
        if not _term_match(text, term):
            return False

    for group in item.get("match_all_groups") or []:
        if isinstance(group, list) and not _contains_any(text, group):
            return False

    return bool(any_terms or item.get("match_all") or item.get("match_all_groups"))


def get_quick_answer(user_text):
    text = norm(user_text)
    answers = sorted(load_answers(), key=lambda x: int(x.get("priority", 0) or 0), reverse=True)
    for item in answers:
        if _matches(item, text):
            lines = item.get("answer_lines") or []
            return "\n".join(str(x) for x in lines) if isinstance(lines, list) else str(lines)
    return None
