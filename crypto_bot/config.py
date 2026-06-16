"""Configuration for the superagrigrator connection.

Values are read from the environment. If a ``.env`` file is present it is
loaded first so local development doesn't require exporting variables by hand.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # python-dotenv is optional at runtime
    pass


class ConfigError(RuntimeError):
    """Raised when required configuration is missing."""


@dataclass(frozen=True)
class Settings:
    """Connection settings for the superagrigrator service."""

    base_url: str
    api_key: str
    timeout: float = 10.0

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from environment variables.

        Raises:
            ConfigError: if a required variable is missing.
        """
        base_url = os.environ.get("SUPERAGRIGRATOR_BASE_URL", "").strip()
        api_key = os.environ.get("SUPERAGRIGRATOR_API_KEY", "").strip()

        missing = [
            name
            for name, value in (
                ("SUPERAGRIGRATOR_BASE_URL", base_url),
                ("SUPERAGRIGRATOR_API_KEY", api_key),
            )
            if not value
        ]
        if missing:
            raise ConfigError(
                "Missing required environment variable(s): "
                + ", ".join(missing)
                + ". Copy .env.example to .env and fill in your values."
            )

        timeout = float(os.environ.get("SUPERAGRIGRATOR_TIMEOUT", "10"))

        return cls(
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            timeout=timeout,
        )
