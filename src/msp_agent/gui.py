from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from pathlib import Path

from .config import load_settings
from .document_processor import document_to_context
from .llm import AIClient
from .learning import add_item, backup as backup_quick_answers, validate as validate_quick_answers
from .quick_answers import get_quick_answer
from .router import choose_model, get_mode, set_mode
from .web_tools import build_research_context


SYSTEM_PROMPT = (
    "You are an MSP-focused AI agent. Use cloud inference first. "
    "Local inference, local SearXNG and local quick answers are fallback or explicit paths only. "
    "Give practical commands, expected results, risks, validation and rollback where relevant."
)


class AgentGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = load_settings(Path.cwd())
        self.root.title("MSP AI Agent — Cloud First")
        self.root.geometry("1180x820")
        self.root.minsize(900, 600)

        self.mode_var = tk.StringVar(value=get_mode())
        self.status_var = tk.StringVar(value="Ready — cloud first")
        self.attached_path: str | None = None
        self.attached_kind: str | None = None
        self.last_query: str = ""
        self.last_answer: str = ""

        self._build()
        self._refresh_status_async()

    def _build(self):
        top = ttk.Frame(self.root, padding=8)
        top.pack(fill=tk.X)

        ttk.Label(top, text="Mode:").pack(side=tk.LEFT)
        mode = ttk.Combobox(
            top,
            textvariable=self.mode_var,
            state="readonly",
            width=12,
            values=["auto", "fast", "deep", "code", "doc", "research", "vision"],
        )
        mode.pack(side=tk.LEFT, padx=(5, 12))
        mode.bind("<<ComboboxSelected>>", self._mode_changed)

        ttk.Button(top, text="Status", command=self._refresh_status_async).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Attach Document", command=self._attach_document).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Attach Image", command=self._attach_image).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Local Quick", command=self._local_quick).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Learn Quick", command=self._learn_quick).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Local Search", command=self._local_search).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Clear", command=self._clear).pack(side=tk.RIGHT, padx=3)

        self.attachment_label = ttk.Label(self.root, text="No attachment", padding=(10, 0))
        self.attachment_label.pack(fill=tk.X)

        self.output = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Consolas", 10))
        self.output.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.output.configure(state=tk.DISABLED)

        input_frame = ttk.Frame(self.root, padding=8)
        input_frame.pack(fill=tk.X)

        self.input = tk.Text(input_frame, height=5, wrap=tk.WORD)
        self.input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input.bind("<Control-Return>", lambda _event: self._send())

        buttons = ttk.Frame(input_frame)
        buttons.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        ttk.Button(buttons, text="Send", command=self._send, width=14).pack(fill=tk.X, pady=(0, 4))
        ttk.Button(buttons, text="Research", command=lambda: self._send(force_context="research"), width=14).pack(fill=tk.X)

        status = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=4)
        status.pack(fill=tk.X)

        self._append(
            "SYSTEM",
            "MSP AI Agent v1.3.1\n"
            "Default interface: GUI\n"
            "Provider priority: cloud -> local fallback\n"
            "Ctrl+Enter sends the current message.",
        )

    def _append(self, role: str, text: str):
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, f"\n[{role}]\n{text}\n")
        self.output.see(tk.END)
        self.output.configure(state=tk.DISABLED)

    def _mode_changed(self, _event=None):
        try:
            set_mode(self.mode_var.get())
            self.status_var.set(f"Mode set to {self.mode_var.get()}")
        except Exception as exc:
            messagebox.showerror("Mode error", str(exc))

    def _clear(self):
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.configure(state=tk.DISABLED)
        self.attached_path = None
        self.attached_kind = None
        self.attachment_label.configure(text="No attachment")

    def _attach_document(self):
        path = filedialog.askopenfilename(
            title="Attach document",
            filetypes=[
                ("Supported documents", "*.txt *.md *.log *.json *.csv *.pdf *.docx *.xlsx *.pptx *.ps1 *.py *.xml *.html"),
                ("All files", "*.*"),
            ],
        )
        if path:
            self.attached_path = path
            self.attached_kind = "document"
            self.attachment_label.configure(text=f"Document: {path}")

    def _attach_image(self):
        path = filedialog.askopenfilename(
            title="Attach image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff"), ("All files", "*.*")],
        )
        if path:
            self.attached_path = path
            self.attached_kind = "vision"
            self.attachment_label.configure(text=f"Image: {path}")

    def _get_query(self) -> str:
        return self.input.get("1.0", tk.END).strip()

    def _send(self, force_context: str | None = None):
        query = self._get_query()
        if not query:
            return

        self.input.delete("1.0", tk.END)
        self.last_query = query
        self._append("YOU", query)
        self.status_var.set("Working…")

        def worker():
            try:
                context = force_context or "chat"
                prompt = query

                if self.attached_kind == "document" and self.attached_path:
                    context = "document"
                    prompt = document_to_context(
                        self.attached_path,
                        query,
                        self.settings.document_max_chars,
                        self.settings.tesseract_cmd,
                    )
                elif self.attached_kind == "vision" and self.attached_path:
                    context = "vision"

                route = choose_model(query, self.settings, context)
                client = AIClient(self.settings, route)

                if context == "vision" and self.attached_path:
                    answer = client.vision(self.attached_path, query)
                else:
                    answer = client.chat([
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt},
                    ])

                self.last_answer = answer
                provider = client.last_provider or "unknown"
                self.root.after(0, self._append, f"AGENT · {provider.upper()}", answer)
                self.root.after(
                    0,
                    self.status_var.set,
                    f"Ready — provider: {provider} | route: {route.task} | cloud: {route.cloud_model} | local fallback: {route.local_model}",
                )
            except Exception as exc:
                self.root.after(0, self._append, "ERROR", str(exc))
                self.root.after(0, self.status_var.set, "Error — see conversation pane")

        threading.Thread(target=worker, daemon=True).start()

    def _local_quick(self):
        query = self._get_query()
        if not query:
            messagebox.showinfo("Local Quick", "Enter a question first.")
            return
        answer = get_quick_answer(query)
        if answer:
            self._append("LOCAL QUICK", answer)
            self.status_var.set("Answered from local quick-answer database")
        else:
            self._append("LOCAL QUICK", "No local quick answer matched.")
            self.status_var.set("No local quick-answer match")

    def _learn_quick(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Learn Quick Answer")
        dialog.geometry("720x560")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Title").pack(anchor="w")
        title = ttk.Entry(frame)
        title.pack(fill=tk.X, pady=(0, 8))
        title.insert(0, (self.last_query or self._get_query() or "Custom quick answer")[:120])

        ttk.Label(frame, text="Trigger aliases (comma-separated; any one may match)").pack(anchor="w")
        triggers = ttk.Entry(frame)
        triggers.pack(fill=tk.X, pady=(0, 8))
        triggers.insert(0, self.last_query or self._get_query())

        ttk.Label(frame, text="Priority").pack(anchor="w")
        priority = ttk.Entry(frame, width=8)
        priority.pack(anchor="w", pady=(0, 8))
        priority.insert(0, "70")

        ttk.Label(frame, text="Answer").pack(anchor="w")
        answer = tk.Text(frame, height=16, wrap=tk.WORD)
        answer.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        if self.last_answer:
            answer.insert("1.0", self.last_answer)

        buttons = ttk.Frame(frame)
        buttons.pack(fill=tk.X)

        def save():
            title_value = title.get().strip()
            trigger_values = [x.strip() for x in triggers.get().split(",") if x.strip()]
            answer_lines = answer.get("1.0", tk.END).rstrip().splitlines()
            if not title_value or not trigger_values or not any(x.strip() for x in answer_lines):
                messagebox.showwarning("Learn Quick", "Title, at least one trigger, and an answer are required.", parent=dialog)
                return
            try:
                priority_value = int(priority.get().strip() or "70")
            except ValueError:
                messagebox.showwarning("Learn Quick", "Priority must be a number.", parent=dialog)
                return
            try:
                backup_quick_answers()
                item = add_item(title_value, [trigger_values], answer_lines, priority_value)
                self.status_var.set(f"Learned quick answer: {item['id']}")
                self._append("SYSTEM", f"Learned local quick answer: {item['id']}")
                dialog.destroy()
            except Exception as exc:
                messagebox.showerror("Learn Quick", str(exc), parent=dialog)

        ttk.Button(buttons, text="Save Learned Answer", command=save).pack(side=tk.RIGHT)
        ttk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=(0, 8))

    def _local_search(self):
        query = self._get_query()
        if not query:
            messagebox.showinfo("Local Search", "Enter a search query first.")
            return
        if not self.settings.searxng_base_url:
            messagebox.showwarning("Local Search", "SEARXNG_BASE_URL is not configured.")
            return

        self.status_var.set("Running explicit local SearXNG research…")

        def worker():
            try:
                context = build_research_context(
                    self.settings.searxng_base_url,
                    query,
                    self.settings.allow_private_urls,
                    self.settings.online_research_max_results,
                    self.settings.online_research_fetch_top,
                    min(self.settings.local_request_timeout, 30),
                )
                route = choose_model(query, self.settings, "research")
                client = AIClient(self.settings, route)
                answer = client.chat([
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context + "\n\n" + query},
                ])
                self.root.after(0, self._append, "LOCAL SEARCH", answer)
                self.root.after(0, self.status_var.set, f"Local SearXNG used; inference provider: {client.last_provider}")
            except Exception as exc:
                self.root.after(0, self._append, "ERROR", str(exc))
                self.root.after(0, self.status_var.set, "Local search failed")

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_status_async(self):
        self.status_var.set("Checking providers…")

        def worker():
            try:
                route = choose_model("status", self.settings)
                client = AIClient(self.settings, route)
                health = client.health()
                cloud = health["cloud"]
                local = health["local"]
                summary = (
                    f"Cloud configured={cloud['configured']} reachable={cloud['ok']} | "
                    f"Local Ollama reachable={local['ok']} | "
                    f"Circuit open={health['circuit_open']} | "
                    f"Order={','.join(self.settings.ai_provider_order)}"
                )
                self.root.after(0, self.status_var.set, summary)
            except Exception as exc:
                self.root.after(0, self.status_var.set, f"Status check failed: {exc}")

        threading.Thread(target=worker, daemon=True).start()


def main():
    root = tk.Tk()
    AgentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
