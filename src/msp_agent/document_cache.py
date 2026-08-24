from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import hashlib,json
from .document_processor import ParsedDocument,process_document

def _key(path):
    stat=path.stat(); return hashlib.sha256(f"{path}|{stat.st_size}|{stat.st_mtime_ns}".encode()).hexdigest()
def _from_dict(data): return ParsedDocument(data.get("path",""),data.get("name",""),data.get("extension",""),int(data.get("size_bytes",0) or 0),data.get("parser",""),data.get("text",""),data.get("metadata",{}) or {},data.get("notes",[]) or [],bool(data.get("truncated",False)))
def process_document_cached(file_path,root=None,max_chars=16000,tesseract_cmd=None):
    path=Path(file_path).expanduser().resolve(); root=Path(root or Path.cwd()); cache_dir=root/"data"/"cache"/"documents"; cache_dir.mkdir(parents=True,exist_ok=True); cache_file=cache_dir/(_key(path)+".json")
    if cache_file.exists():
        try: return _from_dict(json.loads(cache_file.read_text(encoding="utf-8")))
        except Exception: pass
    doc=process_document(str(path),max_chars=max_chars,tesseract_cmd=tesseract_cmd); cache_file.write_text(json.dumps(asdict(doc),indent=2,ensure_ascii=False),encoding="utf-8"); return doc
