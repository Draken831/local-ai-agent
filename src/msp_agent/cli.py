from __future__ import annotations

import shlex
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from .config import load_settings
from .llm import AIClient, OllamaClient
from .learning import add_item, backup as backup_quick_answers, list_items as list_quick_answers, remove_item, test_item, validate as validate_quick_answers
from .router import choose_model, set_mode, get_mode
from .quick_answers import get_quick_answer
from .web_tools import build_research_context, should_use_online
from .script_policy import SCRIPT_SYSTEM_PROMPT

console = Console()
HELP = """/help /exit /status /models /pull <model> /quick <query>
/mode <auto|fast|deep|code|doc|research|vision|status>
/learn <count|list|test|validate|backup|remove|add>
/search <query> /research <query>
/doc <path> [question] /image <path> [question]
/ingestdoc <path> /searchdocs <query> /docindex /cleardocindex
/script <powershell|linux> <request>
/gui
"""


def system_prompt():
    return (
        "You are an MSP-focused AI agent. Use the cloud provider first and local inference only as fallback. "
        "Give practical commands, expected results, risks, validation and rollback where relevant."
    )


def client_for(settings, text, context="chat"):
    route = choose_model(text, settings, context)
    if settings.dynamic_model_announce:
        console.print(
            f"[dim]Route: {route.route} | cloud={route.cloud_model} | local={route.local_model} | {route.reason}[/dim]"
        )
    return AIClient(settings, route)


def status(settings):
    route = choose_model("status", settings)
    client = AIClient(settings, route)
    health = client.health()
    cloud = health["cloud"]
    local = health["local"]
    console.print(Panel(
        f"Provider order: {', '.join(settings.ai_provider_order)}\n"
        f"Cloud: {'reachable' if cloud['ok'] else cloud['message']}\n"
        f"Cloud configured: {cloud['configured']}\n"
        f"Cloud circuit open: {health['circuit_open']}\n"
        f"Local Ollama: {'reachable' if local['ok'] else local['message']}\n"
        f"Runtime mode: {get_mode()}\n"
        f"Root: {settings.root}",
        title="AI Agent Status",
    ))


def handle_command(command, settings):
    parts = shlex.split(command)
    if not parts:
        return True
    cmd = parts[0].lower()

    if cmd in {"/exit", "/quit"}:
        return False
    if cmd == "/help":
        console.print(HELP)
        return True
    if cmd == "/status":
        status(settings)
        return True
    if cmd in {"/learn", "/qa", "/knowledge"}:
        action = parts[1].lower() if len(parts) > 1 else "help"
        if action == "help":
            console.print("/learn count | list | test <question> | validate | backup | remove <id> | add <title> <triggers> <answer>")
            return True
        if action == "count":
            console.print(f"Quick answers: {len(list_quick_answers())}")
            return True
        if action == "list":
            for item in list_quick_answers():
                console.print(f"{item['priority']:>3}  {item['id']}  {item['title']}")
            return True
        if action == "validate":
            console.print(validate_quick_answers())
            return True
        if action == "backup":
            console.print(f"Backup: {backup_quick_answers()}")
            return True
        if action == "test":
            question = " ".join(parts[2:])
            answer = test_item(question)
            console.print(Markdown(answer) if answer else "[yellow]No quick answer matched.[/yellow]")
            return True
        if action == "remove":
            if len(parts) < 3:
                console.print("Usage: /learn remove <local-override-id>")
            else:
                backup_quick_answers()
                console.print("Removed." if remove_item(parts[2]) else "Not found in local overrides.")
            return True
        if action == "add":
            if len(parts) < 5:
                console.print('Usage: /learn add "Title" "trigger1,trigger2" "answer text"')
                console.print("For multi-line answers, use the GUI Learn Quick button.")
                return True
            title = parts[2]
            triggers = [x.strip() for x in parts[3].split(",") if x.strip()]
            answer = " ".join(parts[4:])
            backup_quick_answers()
            item = add_item(title, [triggers], [answer], 70)
            console.print(f"Added: {item['id']}")
            return True
        console.print("[yellow]Unknown /learn action.[/yellow]")
        return True
    if cmd == "/quick":
        query = " ".join(parts[1:])
        quick = get_quick_answer(query)
        console.print(Markdown(quick) if quick else "[yellow]No local quick answer matched.[/yellow]")
        return True
    if cmd == "/mode":
        if len(parts) == 1 or parts[1].lower() == "status":
            console.print(f"Mode: {get_mode()}")
        else:
            console.print(f"Mode set: {set_mode(parts[1])}")
        return True
    if cmd == "/models":
        local = OllamaClient(settings.ollama_base_url, settings.local_model_fast, settings.local_request_timeout, settings.cloud_max_response_tokens)
        try:
            console.print("\n".join(local.list_models()))
        except Exception as exc:
            console.print(f"[yellow]Local model list unavailable: {exc}[/yellow]")
        return True
    if cmd == "/pull":
        if len(parts) < 2:
            console.print("Usage: /pull <local-ollama-model>")
        else:
            local = OllamaClient(settings.ollama_base_url, settings.local_model_fast, settings.local_request_timeout, settings.cloud_max_response_tokens)
            console.print(local.pull_model(parts[1]))
        return True
    if cmd == "/research":
        query = " ".join(parts[1:])
        client = client_for(settings, query, "research")
        answer = client.chat([{"role": "system", "content": system_prompt()}, {"role": "user", "content": query}])
        console.print(Markdown(answer))
        console.print(f"[dim]Provider used: {client.last_provider}[/dim]")
        return True
    if cmd == "/search":
        query = " ".join(parts[1:])
        if not settings.searxng_base_url:
            console.print("[yellow]Local SearXNG is not configured.[/yellow]")
            return True
        prompt = build_research_context(
            settings.searxng_base_url,
            query,
            settings.allow_private_urls,
            settings.online_research_max_results,
            settings.online_research_fetch_top,
            min(settings.local_request_timeout, 30),
        ) + "\n\n" + query
        client = client_for(settings, query, "research")
        answer = client.chat([{"role": "system", "content": system_prompt()}, {"role": "user", "content": prompt}])
        console.print(Markdown(answer))
        console.print(f"[dim]Provider used: {client.last_provider}; local SearXNG explicitly requested[/dim]")
        return True
    if cmd == "/script":
        if len(parts) < 3:
            console.print("Usage: /script <powershell|linux> <request>")
            return True
        kind = parts[1]
        request = " ".join(parts[2:])
        client = client_for(settings, request, "code")
        answer = client.chat([
            {"role": "system", "content": SCRIPT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Create a {kind} script:\n{request}"},
        ])
        console.print(Markdown(answer))
        return True
    if cmd == "/doc":
        from .document_processor import document_to_context
        if len(parts) < 2:
            console.print("Usage: /doc <path> [question]")
            return True
        path = parts[1]
        question = " ".join(parts[2:]) or "Analyze this document."
        context = document_to_context(path, question, settings.document_max_chars, settings.tesseract_cmd)
        client = client_for(settings, question, "document")
        console.print(Markdown(client.chat([
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": context},
        ])))
        return True
    if cmd == "/image":
        if len(parts) < 2:
            console.print("Usage: /image <path> [question]")
            return True
        path = parts[1]
        question = " ".join(parts[2:]) or "Analyze this image."
        client = client_for(settings, question, "vision")
        console.print(Markdown(client.vision(path, question)))
        return True
    if cmd == "/ingestdoc":
        from .doc_indexer import ingest_document
        console.print(ingest_document(parts[1], settings))
        return True
    if cmd == "/searchdocs":
        from .doc_indexer import search_documents
        query = " ".join(parts[1:])
        for result in search_documents(query, settings):
            console.print(f"[cyan]{result.score:.3f}[/cyan] {result.source_name} {result.chunk_id}\n{result.text[:600]}\n")
        return True
    if cmd == "/docindex":
        from .doc_indexer import stats
        console.print(stats(settings))
        return True
    if cmd == "/cleardocindex":
        from .doc_indexer import clear
        console.print(f"Cleared: {clear(settings)}")
        return True
    if cmd == "/gui":
        console.print(r"Run: .\scripts\run-gui.ps1")
        return True

    console.print(f"[yellow]Unknown command: {cmd}. Type /help.[/yellow]")
    return True


def main():
    settings = load_settings(Path.cwd())
    status(settings)

    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.startswith("/"):
            if not handle_command(user_input, settings):
                break
            continue

        # Strict cloud-first path: do not run local quick-answer or local SearXNG
        # before the cloud provider. Use /quick or /search to invoke those local paths explicitly.
        prompt = user_input
        context = "research" if should_use_online(user_input) else "chat"
        client = client_for(settings, user_input, context)
        answer = client.chat([
            {"role": "system", "content": system_prompt()},
            {"role": "user", "content": prompt},
        ])
        console.print(Markdown(answer))
        console.print(f"[dim]Provider used: {client.last_provider}[/dim]")


if __name__ == "__main__":
    main()
