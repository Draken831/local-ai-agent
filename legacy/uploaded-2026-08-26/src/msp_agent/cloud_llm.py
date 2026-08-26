from __future__ import annotations
import base64
from pathlib import Path
import httpx

class CloudClient:
    """OpenAI-compatible cloud LLM client.

    Works unmodified with any provider that speaks the standard OpenAI
    /chat/completions, /embeddings and /models schema. This file is retained
    only as historical source from the 2026-08-26 upload; the active runtime
    uses src/msp_agent/llm.py.
    """
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int=60, max_tokens: int=900):
        self.base_url=base_url.rstrip("/")
        self.api_key=api_key
        self.model=model
        self.timeout=timeout
        self.max_tokens=max_tokens

    def _headers(self):
        h={"Content-Type":"application/json"}
        if self.api_key: h["Authorization"]=f"Bearer {self.api_key}"
        return h

    def health(self):
        if not self.api_key:
            return False,"No cloud API key configured"
        try:
            r=httpx.get(f"{self.base_url}/models", headers=self._headers(), timeout=10); r.raise_for_status()
            return True,"Cloud API reachable"
        except Exception as e:
            return False,str(e)

    def list_models(self):
        r=httpx.get(f"{self.base_url}/models", headers=self._headers(), timeout=self.timeout); r.raise_for_status()
        return [m.get("id","") for m in r.json().get("data",[]) if m.get("id")]

    def pull_model(self, model):
        return f"Cloud providers don't support pulling models locally; make sure '{model}' is enabled on your provider account."

    def chat(self, messages, model=None, temperature=0.2):
        payload={"model":model or self.model,"messages":messages,"temperature":temperature,"max_tokens":self.max_tokens}
        r=httpx.post(f"{self.base_url}/chat/completions", json=payload, headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return r.json()["choices"][0]["message"].get("content","").strip()

    def embed(self, text, model):
        payload={"model":model,"input":text}
        r=httpx.post(f"{self.base_url}/embeddings", json=payload, headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return [float(x) for x in r.json()["data"][0]["embedding"]]

    def vision(self, image_path, prompt, model):
        b64=base64.b64encode(Path(image_path).expanduser().resolve().read_bytes()).decode("ascii")
        ext=Path(image_path).suffix.lower().lstrip(".") or "png"
        content=[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":f"data:image/{ext};base64,{b64}"}}]
        payload={"model":model,"messages":[{"role":"user","content":content}],"temperature":0.1,"max_tokens":self.max_tokens}
        r=httpx.post(f"{self.base_url}/chat/completions", json=payload, headers=self._headers(), timeout=self.timeout)
        r.raise_for_status()
        return r.json()["choices"][0]["message"].get("content","").strip()
