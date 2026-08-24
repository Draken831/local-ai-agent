from __future__ import annotations
import json,re
from pathlib import Path

def norm(text):
    text=str(text or "").lower()
    for a,b in {"defnder":"defender","defendr":"defender","calender":"calendar","exchnage":"exchange","microsfot":"microsoft","powershel":"powershell","commnad":"command"}.items(): text=text.replace(a,b)
    return re.sub(r"\s+"," ",re.sub(r"[^a-z0-9\s:._/-]"," ",text)).strip()
def path(): return Path.cwd()/"data"/"brain"/"quick_answers.json"
def load_answers():
    if not path().exists(): return []
    try: data=json.loads(path().read_text(encoding="utf-8-sig"))
    except Exception: return []
    return [x for x in data if isinstance(x,dict)] if isinstance(data,list) else []
def save_answers(items): path().parent.mkdir(parents=True,exist_ok=True); path().write_text(json.dumps(items,indent=2,ensure_ascii=False),encoding="utf-8")
def _contains_any(text,terms): return any((term:=norm(x)) and term in text for x in terms)
def _matches(item,text):
    if _contains_any(text,item.get("exclude_any") or []): return False
    any_terms=item.get("match_any") or []
    if any_terms and not _contains_any(text,any_terms): return False
    for term in item.get("match_all") or []:
        if norm(term) not in text: return False
    for group in item.get("match_all_groups") or []:
        if isinstance(group,list) and not _contains_any(text,group): return False
    return bool(any_terms or item.get("match_all") or item.get("match_all_groups"))
def get_quick_answer(user_text):
    text=norm(user_text); answers=sorted(load_answers(),key=lambda x:int(x.get("priority",0) or 0),reverse=True)
    for item in answers:
        if _matches(item,text):
            lines=item.get("answer_lines") or []; return "\n".join(str(x) for x in lines) if isinstance(lines,list) else str(lines)
    return None
