from pathlib import Path
import json

ROOT = Path.cwd()


def test_versions_and_policy_match():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.3.1"' in pyproject
    profile = json.loads((ROOT / "data/brain/agent-profile.json").read_text(encoding="utf-8"))
    policy = json.loads((ROOT / "data/brain/runtime-policy.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "data/brain/tool-registry.json").read_text(encoding="utf-8"))
    assert profile["version"] == "1.3.1"
    assert profile["provider_priority"] == ["cloud", "local"]
    assert profile["interface"] == "GUI-default"
    assert "local-first" not in profile["operating_model"]
    assert policy["provider_priority"] == ["cloud", "local"]
    assert policy["local"]["searxng_precontext_by_default"] is False
    assert registry["provider_priority"] == ["cloud", "local"]
    assert registry["tools"][0]["name"] == "cloud_llm"


def test_current_installer_only_in_active_installer_dir():
    names = sorted(p.name for p in (ROOT / "installers").glob("*.ps1"))
    assert names == ["Install-MSP-AI-Agent-CloudFirst-v1.3.1.ps1"]


def test_current_env_uses_unambiguous_local_search_setting():
    env = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "AI_PROVIDER_ORDER=cloud,local" in env
    assert "LOCAL_SEARXNG_PRECONTEXT=false" in env
    assert "ONLINE_FIRST_MODE=" not in env
