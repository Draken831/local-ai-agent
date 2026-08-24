from __future__ import annotations
import base64, mimetypes, time
from pathlib import Path
import httpx

_CIRCUIT = {"failures": 0, "open_until": 0.0}

class ProviderError(RuntimeError): pass

def _extract_responses_text(data: dict) -> str:
    direct = data.get("output_text")
    if isinstance(direct, str) and direct.strip(): return direct.strip()
    chunks=[]
    for item in data.get("output", []) or []:
        if not isinstance(item, dict): continue
        for content in item.get("content", []) or []:
            if isinstance(content, dict) and content.get("type") in {"output_text","text"}:
                text=content.get("text")
                if isinstance(text, str): chunks.append(text)
    return "\n".join(chunks).strip()

class CloudClient:
    def __init__(self, settings):
        self.settings=settings; self.base_url=settings.cloud_api_base_url.rstrip("/"); self.key=settings.cloud_api_key; self.style=settings.cloud_api_style
    @property
    def configured(self): return bool(self.settings.cloud_ai_enabled and self.base_url and self.key)
    def _timeout(self): return httpx.Timeout(self.settings.cloud_timeout_read,connect=self.settings.cloud_timeout_connect,write=self.settings.cloud_timeout_connect,pool=self.settings.cloud_timeout_connect)
    def _headers(self): return {"Authorization":f"Bearer {self.key}","Content-Type":"application/json"}
    def _post(self,path,payload):
        if not self.configured: raise ProviderError("Cloud provider is not configured. Set CLOUD_API_KEY.")
        last=None; attempts=max(1,self.settings.cloud_retries+1)
        for attempt in range(attempts):
            try:
                r=httpx.post(f"{self.base_url}/{path.lstrip('/')}",headers=self._headers(),json=payload,timeout=self._timeout())
                if r.status_code==429 or r.status_code>=500: raise ProviderError(f"Cloud HTTP {r.status_code}: {r.text[:300]}")
                r.raise_for_status(); data=r.json()
                if not isinstance(data,dict): raise ProviderError("Cloud provider returned non-object JSON.")
                return data
            except (httpx.TimeoutException,httpx.NetworkError,ProviderError,httpx.HTTPStatusError) as exc:
                last=exc
                if attempt+1<attempts: time.sleep(0.25*(attempt+1))
        raise ProviderError(str(last) if last else "Cloud request failed.")
    def health(self):
        if not self.configured: return False,"not configured"
        try:
            r=httpx.get(f"{self.base_url}/models",headers=self._headers(),timeout=httpx.Timeout(5,connect=self.settings.cloud_timeout_connect)); r.raise_for_status(); return True,"reachable"
        except Exception as exc: return False,str(exc)
    def _split_messages(self,messages):
        instructions=[]; conversation=[]
        for msg in messages:
            role=str(msg.get("role","user")); content=str(msg.get("content",""))
            if role=="system": instructions.append(content)
            else: conversation.append(f"{role.upper()}: {content}")
        return "\n\n".join(instructions),"\n\n".join(conversation)
    def chat(self,messages,model,temperature=0.2):
        if self.style=="chat_completions":
            data=self._post("chat/completions",{"model":model,"messages":messages,"temperature":temperature,"max_tokens":self.settings.cloud_max_response_tokens})
            return str(data["choices"][0]["message"]["content"]).strip()
        instructions,prompt=self._split_messages(messages); payload={"model":model,"input":prompt,"max_output_tokens":self.settings.cloud_max_response_tokens}
        if instructions: payload["instructions"]=instructions
        text=_extract_responses_text(self._post("responses",payload))
        if not text: raise ProviderError("Cloud Responses API returned no output text.")
        return text
    def vision(self,image_path,prompt,model):
        path=Path(image_path).expanduser().resolve(); mime=mimetypes.guess_type(path.name)[0] or "image/png"; data_url=f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"
        if self.style=="chat_completions":
            data=self._post("chat/completions",{"model":model,"messages":[{"role":"user","content":[{"type":"text","text":prompt},{"type":"image_url","image_url":{"url":data_url}}]}],"max_tokens":self.settings.cloud_max_response_tokens})
            return str(data["choices"][0]["message"]["content"]).strip()
        text=_extract_responses_text(self._post("responses",{"model":model,"input":[{"role":"user","content":[{"type":"input_text","text":prompt},{"type":"input_image","image_url":data_url}]}],"max_output_tokens":self.settings.cloud_max_response_tokens}))
        if not text: raise ProviderError("Cloud vision returned no output text.")
        return text
    def embed(self,text,model):
        data=self._post("embeddings",{"model":model,"input":text})
        return [float(x) for x in data["data"][0]["embedding"]]

class OllamaClient:
    def __init__(self,base_url,model,timeout=180,max_tokens=900): self.base_url=base_url.rstrip("/"); self.model=model; self.timeout=timeout; self.max_tokens=max_tokens
    def health(self):
        try: r=httpx.get(f"{self.base_url}/api/tags",timeout=5); r.raise_for_status(); return True,"reachable"
        except Exception as exc: return False,str(exc)
    def list_models(self):
        r=httpx.get(f"{self.base_url}/api/tags",timeout=self.timeout); r.raise_for_status(); return [m.get("name","") for m in r.json().get("models",[]) if m.get("name")]
    def pull_model(self,model):
        r=httpx.post(f"{self.base_url}/api/pull",json={"name":model,"stream":False},timeout=None); r.raise_for_status(); return r.text[:1000]
    def chat(self,messages,model=None,temperature=0.2):
        r=httpx.post(f"{self.base_url}/api/chat",json={"model":model or self.model,"messages":messages,"stream":False,"options":{"temperature":temperature,"num_predict":self.max_tokens}},timeout=self.timeout); r.raise_for_status(); return r.json().get("message",{}).get("content","").strip()
    def embed(self,text,model):
        try:
            r=httpx.post(f"{self.base_url}/api/embed",json={"model":model,"input":text},timeout=self.timeout); r.raise_for_status(); e=r.json().get("embeddings")
            if isinstance(e,list) and e: return [float(x) for x in e[0]]
        except Exception: pass
        r=httpx.post(f"{self.base_url}/api/embeddings",json={"model":model,"prompt":text},timeout=self.timeout); r.raise_for_status(); return [float(x) for x in r.json().get("embedding",[])]
    def vision(self,image_path,prompt,model):
        b64=base64.b64encode(Path(image_path).expanduser().resolve().read_bytes()).decode("ascii"); r=httpx.post(f"{self.base_url}/api/chat",json={"model":model,"stream":False,"messages":[{"role":"user","content":prompt,"images":[b64]}],"options":{"temperature":0.1,"num_predict":self.max_tokens}},timeout=self.timeout); r.raise_for_status(); return r.json().get("message",{}).get("content","").strip()

class AIClient:
    def __init__(self,settings,route):
        self.settings=settings; self.route=route; self.cloud=CloudClient(settings); self.local=OllamaClient(settings.ollama_base_url,route.local_model,settings.local_request_timeout,settings.cloud_max_response_tokens); self.last_provider=None; self.last_error=None
    @property
    def model(self): return self.route.cloud_model if self._cloud_allowed() else self.route.local_model
    def _cloud_allowed(self): return "cloud" in self.settings.ai_provider_order and self.cloud.configured and time.monotonic()>=float(_CIRCUIT["open_until"])
    def _cloud_failed(self,exc):
        self.last_error=str(exc); _CIRCUIT["failures"]=int(_CIRCUIT["failures"])+1
        if int(_CIRCUIT["failures"])>=max(1,self.settings.cloud_circuit_breaker_failures): _CIRCUIT["open_until"]=time.monotonic()+max(1,self.settings.cloud_circuit_breaker_seconds)
    def _cloud_succeeded(self): _CIRCUIT["failures"]=0; _CIRCUIT["open_until"]=0.0; self.last_error=None
    def health(self):
        cloud_ok,cloud_msg=self.cloud.health(); local_ok,local_msg=self.local.health(); return {"cloud":{"ok":cloud_ok,"message":cloud_msg,"configured":self.cloud.configured},"local":{"ok":local_ok,"message":local_msg},"circuit_open":time.monotonic()<float(_CIRCUIT["open_until"])}
    def chat(self,messages,temperature=0.2):
        errors=[]
        for provider in self.settings.ai_provider_order:
            if provider=="cloud" and self._cloud_allowed():
                try: answer=self.cloud.chat(messages,self.route.cloud_model,temperature); self._cloud_succeeded(); self.last_provider="cloud"; return answer
                except Exception as exc: self._cloud_failed(exc); errors.append(f"cloud: {exc}")
            elif provider=="local" and self.settings.local_fallback_enabled:
                try: answer=self.local.chat(messages,self.route.local_model,temperature); self.last_provider="local"; return answer
                except Exception as exc: errors.append(f"local: {exc}")
        raise ProviderError("All configured providers failed: "+" | ".join(errors))
    def vision(self,image_path,prompt):
        errors=[]
        for provider in self.settings.ai_provider_order:
            if provider=="cloud" and self._cloud_allowed():
                try: answer=self.cloud.vision(image_path,prompt,self.route.cloud_model); self._cloud_succeeded(); self.last_provider="cloud"; return answer
                except Exception as exc: self._cloud_failed(exc); errors.append(f"cloud: {exc}")
            elif provider=="local" and self.settings.local_fallback_enabled:
                try: answer=self.local.vision(image_path,prompt,self.route.local_model); self.last_provider="local"; return answer
                except Exception as exc: errors.append(f"local: {exc}")
        raise ProviderError("All configured vision providers failed: "+" | ".join(errors))
    def embed(self,text):
        if self.settings.cloud_embeddings_enabled and self._cloud_allowed():
            try: result=self.cloud.embed(text,self.settings.cloud_embedding_model); self._cloud_succeeded(); self.last_provider="cloud"; return result
            except Exception as exc: self._cloud_failed(exc)
        if self.settings.local_fallback_enabled: self.last_provider="local"; return self.local.embed(text,self.settings.local_embedding_model)
        raise ProviderError("No embedding provider is available.")
