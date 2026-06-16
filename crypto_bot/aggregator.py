"""HTTP client for the superagrigrator service.

All knowledge of the remote API (paths, auth header, response shape) lives in
this module. If the real superagrigrator endpoints differ, this is the only
file that needs to change.
"""

from __future__ import annotations

from typing import Any

import requests

from .config import Settings


class SuperagrigratorError(RuntimeError):
    """Raised when a request to superagrigrator fails."""


class SuperagrigratorClient:
    """A thin client around the superagrigrator HTTP API."""

    def __init__(self, settings: Settings, session: requests.Session | None = None):
        self._settings = settings
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {settings.api_key}",
                "Accept": "application/json",
                "User-Agent": "crypto-bot/0.1",
            }
        )

    # -- internals --------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self._settings.base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            resp = self._session.request(
                method,
                self._url(path),
                timeout=self._settings.timeout,
                **kwargs,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise SuperagrigratorError(
                f"{method} {path} failed: {exc}"
            ) from exc

        if not resp.content:
            return None
        return resp.json()

    # -- public API -------------------------------------------------------

    def health_check(self) -> bool:
        """Return True if superagrigrator is reachable and authenticated."""
        try:
            self._request("GET", "/health")
            return True
        except SuperagrigratorError:
            return False

    def get_price(self, symbol: str) -> dict[str, Any]:
        """Fetch the latest aggregated price for ``symbol`` (e.g. 'BTC-USD')."""
        return self._request("GET", f"/prices/{symbol}")

    def place_order(self, order: dict[str, Any]) -> dict[str, Any]:
        """Submit an order to superagrigrator for routing/execution."""
        return self._request("POST", "/orders", json=order)
