from __future__ import annotations
import threading
import tkinter as tk
from tkinter import scrolledtext
from pathlib import Path

from .config import load_settings
from .llm import AIClient
from .router import choose_model


def main():
    settings = load_settings(Path.cwd())
    root = tk.Tk()
    root.title("MSP AI Agent — Cloud First")
    root.geometry("1100x750")

    output = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    output.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    frame = tk.Frame(root)
    frame.pack(fill=tk.X, padx=8, pady=8)
    entry = tk.Entry(frame)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def append(text):
        output.insert(tk.END, text + "\n")
        output.see(tk.END)

    def send():
        query = entry.get().strip()
        if not query:
            return
        entry.delete(0, tk.END)
        append("You: " + query)

        def worker():
            try:
                route = choose_model(query, settings)
                client = AIClient(settings, route)
                answer = client.chat([
                    {"role": "system", "content": "You are an MSP-focused AI agent. Cloud first; local inference is fallback only."},
                    {"role": "user", "content": query},
                ])
                root.after(0, append, f"Agent [{client.last_provider}]:\n{answer}")
            except Exception as exc:
                root.after(0, append, "Error: " + str(exc))

        threading.Thread(target=worker, daemon=True).start()

    button = tk.Button(frame, text="Send", command=send)
    button.pack(side=tk.RIGHT, padx=(8, 0))
    entry.bind("<Return>", lambda _event: send())
    root.mainloop()


if __name__ == "__main__":
    main()
