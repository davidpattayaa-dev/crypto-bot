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


# The superaggregator instance the bot talks to by default. It's an open
# endpoint (no login required), so the bot works out of the box.
DEFAULT_BASE_URL = "https://superaggregator.fly.dev"


@dataclass(frozen=True)
class Settings:
    """Connection settings for the superaggregator service."""

    base_url: str = DEFAULT_BASE_URL
    api_key: str = ""  # optional: the public instance needs no auth
    timeout: float = 10.0
    retries: int = 2  # extra attempts on transient network errors
    backoff: float = 0.5  # base seconds for exponential backoff between retries

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings from environment variables.

        Only the base URL is needed, and it defaults to the public instance,
        so no configuration is required for the open endpoint. An API key is
        optional and only sent if provided.
        """
        base_url = (
            os.environ.get("SUPERAGRIGRATOR_BASE_URL", "").strip()
            or DEFAULT_BASE_URL
        )
        api_key = os.environ.get("SUPERAGRIGRATOR_API_KEY", "").strip()
        timeout = float(os.environ.get("SUPERAGRIGRATOR_TIMEOUT", "10"))
        retries = int(os.environ.get("SUPERAGRIGRATOR_RETRIES", "2"))
        backoff = float(os.environ.get("SUPERAGRIGRATOR_BACKOFF", "0.5"))

        return cls(
            base_url=base_url.rstrip("/"),
            api_key=api_key,
            timeout=timeout,
            retries=retries,
            backoff=backoff,
        )
