from __future__ import annotations
import shlex
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from .config import load_settings
from .llm import AIClient, OllamaClient
from .router import choose_model,set_mode,get_mode
from .quick_answers import get_quick_answer
from .web_tools import build_research_context,should_use_online
from .script_policy import SCRIPT_SYSTEM_PROMPT

console=Console()
HELP="""/help /exit /status /models /pull <model>\n/mode <auto|fast|deep|code|doc|research|vision|status>\n/research <query> /doc <path> [question] /image <path> [question]\n/ingestdoc <path> /searchdocs <query> /docindex /cleardocindex\n/script <powershell|linux> <request> /gui\n"""

def system_prompt(): return "You are an MSP-focused AI agent. Use cloud inference first and local inference only as fallback. Give practical commands, expected results, risks, validation and rollback where relevant."
def client_for(settings,text,context="chat"):
    route=choose_model(text,settings,context)
    if settings.dynamic_model_announce: console.print(f"[dim]Route: {route.route} | cloud={route.cloud_model} | local={route.local_model} | {route.reason}[/dim]")
    return AIClient(settings,route)
def status(settings):
    client=AIClient(settings,choose_model("status",settings)); health=client.health(); cloud=health["cloud"]; local=health["local"]
    console.print(Panel(f"Provider order: {', '.join(settings.ai_provider_order)}\nCloud: {'reachable' if cloud['ok'] else cloud['message']}\nCloud configured: {cloud['configured']}\nCloud circuit open: {health['circuit_open']}\nLocal Ollama: {'reachable' if local['ok'] else local['message']}\nRuntime mode: {get_mode()}\nRoot: {settings.root}",title="AI Agent Status"))
def handle_command(command,settings):
    parts=shlex.split(command)
    if not parts: return True
    cmd=parts[0].lower()
    if cmd in {"/exit","/quit"}: return False
    if cmd=="/help": console.print(HELP); return True
    if cmd=="/status": status(settings); return True
    if cmd=="/mode":
        if len(parts)==1 or parts[1].lower()=="status": console.print(f"Mode: {get_mode()}")
        else: console.print(f"Mode set: {set_mode(parts[1])}")
        return True
    if cmd=="/models":
        local=OllamaClient(settings.ollama_base_url,settings.local_model_fast,settings.local_request_timeout,settings.cloud_max_response_tokens)
        try: console.print("\n".join(local.list_models()))
        except Exception as exc: console.print(f"[yellow]Local model list unavailable: {exc}[/yellow]")
        return True
    if cmd=="/pull":
        local=OllamaClient(settings.ollama_base_url,settings.local_model_fast,settings.local_request_timeout,settings.cloud_max_response_tokens); console.print(local.pull_model(parts[1])); return True
    if cmd in {"/research","/search"}:
        query=" ".join(parts[1:]); prompt=query
        if settings.searxng_base_url:
            try: prompt=build_research_context(settings.searxng_base_url,query,settings.allow_private_urls,settings.online_research_max_results,settings.online_research_fetch_top,min(settings.local_request_timeout,30))+"\n\n"+query
            except Exception as exc: console.print(f"[yellow]Research fetch failed; using cloud model directly: {exc}[/yellow]")
        client=client_for(settings,query,"research"); console.print(Markdown(client.chat([{"role":"system","content":system_prompt()},{"role":"user","content":prompt}]))); return True
    if cmd=="/script":
        kind=parts[1]; request=" ".join(parts[2:]); client=client_for(settings,request,"code"); console.print(Markdown(client.chat([{"role":"system","content":SCRIPT_SYSTEM_PROMPT},{"role":"user","content":f"Create a {kind} script:\n{request}"}]))); return True
    if cmd=="/doc":
        from .document_processor import document_to_context
        path=parts[1]; question=" ".join(parts[2:]) or "Analyze this document."; context=document_to_context(path,question,settings.document_max_chars,settings.tesseract_cmd); client=client_for(settings,question,"document"); console.print(Markdown(client.chat([{"role":"system","content":system_prompt()},{"role":"user","content":context}]))); return True
    if cmd=="/image":
        path=parts[1]; question=" ".join(parts[2:]) or "Analyze this image."; client=client_for(settings,question,"vision"); console.print(Markdown(client.vision(path,question))); return True
    if cmd=="/ingestdoc":
        from .doc_indexer import ingest_document; console.print(ingest_document(parts[1],settings)); return True
    if cmd=="/searchdocs":
        from .doc_indexer import search_documents
        for result in search_documents(" ".join(parts[1:]),settings): console.print(f"[cyan]{result.score:.3f}[/cyan] {result.source_name} {result.chunk_id}\n{result.text[:600]}\n")
        return True
    if cmd=="/docindex":
        from .doc_indexer import stats; console.print(stats(settings)); return True
    if cmd=="/cleardocindex":
        from .doc_indexer import clear; console.print(f"Cleared: {clear(settings)}"); return True
    if cmd=="/gui": console.print(r"Run: .\scripts\run-gui.ps1"); return True
    console.print(f"[yellow]Unknown command: {cmd}. Type /help.[/yellow]"); return True

def main():
    settings=load_settings(Path.cwd()); status(settings)
    while True:
        try: user_input=console.input("[bold cyan]You:[/bold cyan] ").strip()
        except (EOFError,KeyboardInterrupt): console.print("\nExiting."); break
        if not user_input: continue
        if user_input.startswith("/"):
            if not handle_command(user_input,settings): break
            continue
        quick=get_quick_answer(user_input)
        if quick: console.print(Markdown(quick)); continue
        prompt=user_input
        if settings.online_first_mode and settings.searxng_base_url and should_use_online(user_input):
            try: prompt=build_research_context(settings.searxng_base_url,user_input,settings.allow_private_urls,settings.online_research_max_results,settings.online_research_fetch_top,min(settings.local_request_timeout,30))+"\n\n"+user_input
            except Exception as exc: console.print(f"[yellow]Research source failed; continuing with cloud inference: {exc}[/yellow]")
        client=client_for(settings,user_input); answer=client.chat([{"role":"system","content":system_prompt()},{"role":"user","content":prompt}]); console.print(Markdown(answer)); console.print(f"[dim]Provider used: {client.last_provider}[/dim]")

if __name__=="__main__": main()
