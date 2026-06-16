"""Tests for environment-driven configuration."""

import pytest

from crypto_bot.config import ConfigError, Settings


def test_from_env_ok(monkeypatch):
    monkeypatch.setenv("SUPERAGRIGRATOR_BASE_URL", "https://api.example/")
    monkeypatch.setenv("SUPERAGRIGRATOR_API_KEY", "k")
    monkeypatch.setenv("SUPERAGRIGRATOR_TIMEOUT", "3")

    settings = Settings.from_env()

    assert settings.base_url == "https://api.example"  # trailing slash stripped
    assert settings.api_key == "k"
    assert settings.timeout == 3.0


def test_from_env_missing_raises(monkeypatch):
    monkeypatch.delenv("SUPERAGRIGRATOR_BASE_URL", raising=False)
    monkeypatch.delenv("SUPERAGRIGRATOR_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        Settings.from_env()
