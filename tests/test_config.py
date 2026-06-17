"""Tests for environment-driven configuration."""

import pytest

from crypto_bot.config import DEFAULT_BASE_URL, Settings


def test_from_env_ok(monkeypatch):
    monkeypatch.setenv("SUPERAGRIGRATOR_BASE_URL", "https://api.example/")
    monkeypatch.setenv("SUPERAGRIGRATOR_API_KEY", "k")
    monkeypatch.setenv("SUPERAGRIGRATOR_TIMEOUT", "3")

    settings = Settings.from_env()

    assert settings.base_url == "https://api.example"  # trailing slash stripped
    assert settings.api_key == "k"
    assert settings.timeout == 3.0


def test_from_env_defaults_to_public_instance(monkeypatch):
    # No config at all -> open public instance, no key required.
    monkeypatch.delenv("SUPERAGRIGRATOR_BASE_URL", raising=False)
    monkeypatch.delenv("SUPERAGRIGRATOR_API_KEY", raising=False)
    monkeypatch.delenv("SUPERAGRIGRATOR_TIMEOUT", raising=False)

    settings = Settings.from_env()

    assert settings.base_url == DEFAULT_BASE_URL
    assert settings.api_key == ""
