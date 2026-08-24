from __future__ import annotations
from dataclasses import dataclass
import hashlib,json,math
from .document_cache import process_document_cached
from .llm import AIClient
from .router import choose_model

@dataclass
class SearchResult:
    score: float; source_name: str; source_path: str; chunk_id: str; text: str

def index_path(root):
    path=root/"data"/"vectorstore"/"doc_chunks.jsonl"; path.parent.mkdir(parents=True,exist_ok=True); return path

def chunks(text,size=1200,overlap=150):
    out=[]; start=0; text=text.strip()
    while start<len(text):
        end=min(start+size,len(text)); out.append(text[start:end].strip())
        if end>=len(text): break
        start=max(0,end-overlap)
    return [x for x in out if x]

def load(root):
    path=index_path(root); rows=[]
    if not path.exists(): return rows
    for line in path.read_text(encoding="utf-8",errors="ignore").splitlines():
        try: rows.append(json.loads(line))
        except Exception: pass
    return rows

def write(root,rows):
    with index_path(root).open("w",encoding="utf-8") as handle:
        for row in rows: handle.write(json.dumps(row,ensure_ascii=False)+"\n")

def _embedder(settings): return AIClient(settings,choose_model("document embedding",settings,"document"))

def ingest_document(file_path,settings):
    doc=process_document_cached(file_path,settings.root,settings.document_max_chars,settings.tesseract_cmd); source_hash=hashlib.sha256((doc.path+str(doc.size_bytes)+doc.text[:1000]).encode()).hexdigest(); rows=[r for r in load(settings.root) if r.get("source_hash")!=source_hash]; client=_embedder(settings); added=[]
    for index,chunk in enumerate(chunks(doc.text),1): added.append({"chunk_id":f"{source_hash[:12]}-{index:04d}","source_hash":source_hash,"source_name":doc.name,"source_path":doc.path,"chunk_index":index,"text":chunk,"embedding":client.embed(chunk)})
    write(settings.root,rows+added); return {"source":doc.name,"chunks_added":len(added),"total_chunks":len(rows)+len(added),"provider":client.last_provider}

def _cos(a,b):
    if not a or not b or len(a)!=len(b): return 0.0
    dot=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(y*y for y in b)); return 0.0 if na==0 or nb==0 else dot/(na*nb)

def search_documents(query,settings,top_k=5):
    rows=load(settings.root)
    if not rows: return []
    client=_embedder(settings); qe=client.embed(query); out=[]
    for row in rows:
        embedding=row.get("embedding")
        if isinstance(embedding,list): out.append(SearchResult(_cos(qe,[float(x) for x in embedding]),row.get("source_name",""),row.get("source_path",""),row.get("chunk_id",""),row.get("text","")))
    return sorted(out,key=lambda x:x.score,reverse=True)[:top_k]

def stats(settings):
    rows=load(settings.root); sources=sorted({r.get("source_path","") for r in rows if r.get("source_path")}); return {"index_path":str(index_path(settings.root)),"chunk_count":len(rows),"source_count":len(sources),"sources":sources}

def clear(settings): path=index_path(settings.root); path.write_text("",encoding="utf-8"); return path
