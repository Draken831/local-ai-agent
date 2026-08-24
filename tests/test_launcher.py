from pathlib import Path


def test_run_ps1_launches_default_gui_launcher():
    text = (Path.cwd() / "scripts" / "run.ps1").read_text(encoding="utf-8")
    assert "-m msp_agent.launcher" in text
    assert "--cli" not in text


def test_cli_is_explicit():
    text = (Path.cwd() / "scripts" / "run-cli.ps1").read_text(encoding="utf-8")
    assert "--cli" in text


def test_pyproject_default_command_uses_launcher():
    text = (Path.cwd() / "pyproject.toml").read_text(encoding="utf-8")
    assert 'msp-agent = "msp_agent.launcher:main"' in text
