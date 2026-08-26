from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import re
import shutil

from .quick_answers import get_quick_answer, load_answers, path


def slug(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", str(value).lower()).strip("_")
    return re.sub(r"_+", "_", value)[:60] or "custom_answer"


def _load_local() -> list[dict]:
    p = path()
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        return []
    return [x for x in data if isinstance(x, dict)] if isinstance(data, list) else []


def _save_local(items: list[dict]) -> None:
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def backup() -> Path:
    p = path()
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("[]\n", encoding="utf-8")
    destination = p.parent / "backups"
    destination.mkdir(parents=True, exist_ok=True)
    out = destination / f"quick_answers.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    shutil.copy2(p, out)
    return out


def list_items() -> list[dict]:
    return sorted(
        [
            {
                "id": x.get("id", ""),
                "title": x.get("title", ""),
                "priority": int(x.get("priority", 0) or 0),
            }
            for x in load_answers()
        ],
        key=lambda x: x["priority"],
        reverse=True,
    )


def validate() -> dict:
    items = load_answers()
    local = _load_local()
    seen = set()
    duplicates = []
    missing = []

    for index, item in enumerate(items):
        item_id = item.get("id")
        if not item_id:
            missing.append(f"{index}: missing id")
        elif item_id in seen:
            duplicates.append(item_id)
        seen.add(item_id)
        if not item.get("answer_lines"):
            missing.append(f"{item_id or index}: missing answer_lines")

    return {
        "path": str(path()),
        "local_override_count": len(local),
        "effective_count": len(items),
        "duplicate_ids": duplicates,
        "missing_required": missing,
    }


def add_item(title: str, groups: list[list[str]], lines: list[str], priority: int = 70) -> dict:
    local = _load_local()
    item = {
        "id": f"qa.custom.{slug(title)}.{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "title": title,
        "priority": int(priority),
        "match_all_groups": groups,
        "exclude_any": ["latest", "current", "online", "research"],
        "answer_lines": lines,
    }
    local.append(item)
    _save_local(local)
    return item


def remove_item(item_id: str) -> bool:
    local = _load_local()
    updated = [x for x in local if x.get("id") != item_id]
    if len(updated) == len(local):
        return False
    _save_local(updated)
    return True


def test_item(question: str):
    return get_quick_answer(question)
