from msp_agent.config import load_settings
from msp_agent.router import choose_model


def test_provider_order_defaults_cloud_first(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_PROVIDER_ORDER", raising=False)
    settings = load_settings(tmp_path)
    assert settings.ai_provider_order == ("cloud", "local")


def test_cloud_web_search_defaults_enabled(tmp_path):
    settings = load_settings(tmp_path)
    assert settings.cloud_web_search_enabled is True
    assert settings.online_first_mode is False


def test_current_info_routes_to_cloud_research_path(tmp_path):
    settings = load_settings(tmp_path)
    route = choose_model("latest Microsoft release notes", settings)
    assert route.task == "research"
    assert route.cloud_model
    assert route.local_model


def test_router_returns_cloud_and_local_code_models(tmp_path):
    settings = load_settings(tmp_path)
    route = choose_model("Write a PowerShell script", settings, "code")
    assert route.task == "code"
    assert route.cloud_model
    assert route.local_model


def test_old_v4_model_names_remain_local_fallback(tmp_path):
    (tmp_path / ".env").write_text(
        "MODEL_FAST=legacy-fast\nMODEL_CODE=legacy-code\nOLLAMA_MODEL=legacy-default\n",
        encoding="utf-8",
    )
    settings = load_settings(tmp_path)
    assert settings.local_model_fast == "legacy-fast"
    assert settings.local_model_code == "legacy-code"
