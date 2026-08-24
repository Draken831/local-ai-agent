from pathlib import Path
import json

import msp_agent.quick_answers as qa


def test_natural_variations_match(tmp_path, monkeypatch):
    source = Path.cwd() / "data" / "brain" / "quick_answers.json"
    monkeypatch.setattr(qa, "path", lambda: source)

    checks = {
        "How do I force an Entra sync?": "Start-ADSyncSyncCycle",
        "Windows updates are stuck; clear the Windows Update cache": "SoftwareDistribution.old",
        "How do I test if TCP 443 is open?": "Test-NetConnection",
        "Is this agent cloud first or local first?": "cloud first",
        "How do I run the AI agent GUI?": "run-gui.ps1",
        "shared mailbox crashes classic Outlook": "Download shared folders",
    }

    for prompt, expected in checks.items():
        answer = qa.get_quick_answer(prompt)
        assert answer is not None, prompt
        assert expected.lower() in answer.lower(), prompt
