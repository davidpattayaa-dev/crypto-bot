"""HTTP client for the superaggregator service.

All knowledge of the remote API (paths, auth header, response shape) lives in
this module. If the real superaggregator endpoints differ, this is the only
file that needs to change.
"""

from __future__ import annotations

import time
from typing import Any

import requests

from .config import Settings

# Transient errors worth retrying (network blips, timeouts).
_RETRYABLE = (requests.ConnectionError, requests.Timeout)

# Candidate paths probed by ``discover()`` to learn the real API surface.
_CANDIDATE_PATHS = (
    "/",
    "/health",
    "/healthz",
    "/api",
    "/api/health",
    "/chart",
    "/api/chart",
    "/prices",
    "/api/prices",
    "/candles",
    "/api/candles",
    "/symbols",
    "/api/symbols",
)


class SuperagrigratorError(RuntimeError):
    """Raised when a request to superaggregator fails."""


class EgressBlockedError(SuperagrigratorError):
    """Raised when the network policy blocks the host (not the site's fault).

    This happens when the current environment's egress allowlist does not
    include the superaggregator host. The fix is to add the host to the
    environment's network settings, not to change the code.
    """


class SuperagrigratorClient:
    """A thin client around the superaggregator HTTP API."""

    def __init__(self, settings: Settings, session: requests.Session | None = None):
        self._settings = settings
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "crypto-bot/0.1",
            }
        )
        # The public instance needs no auth; only send a key if one is set.
        if settings.api_key:
            self._session.headers["Authorization"] = f"Bearer {settings.api_key}"

    # -- internals --------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self._settings.base_url}/{path.lstrip('/')}"

    def _raw_request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        """Perform a request with retries, returning the raw response.

        Raises:
            EgressBlockedError: if the environment's network policy blocks the host.
            SuperagrigratorError: on any other failure (after exhausting retries).
        """
        attempts = self._settings.retries + 1
        last_exc: Exception | None = None

        for attempt in range(attempts):
            try:
                resp = self._session.request(
                    method,
                    self._url(path),
                    timeout=self._settings.timeout,
                    **kwargs,
                )
            except _RETRYABLE as exc:
                last_exc = exc
                if attempt < attempts - 1:
                    time.sleep(self._settings.backoff * (2**attempt))
                    continue
                raise SuperagrigratorError(
                    f"{method} {path} failed after {attempts} attempt(s): {exc}"
                ) from exc
            except requests.RequestException as exc:
                raise SuperagrigratorError(f"{method} {path} failed: {exc}") from exc

            self._raise_for_egress_block(resp)
            return resp

        # Unreachable, but keeps type-checkers happy.
        raise SuperagrigratorError(f"{method} {path} failed: {last_exc}")

    @staticmethod
    def _raise_for_egress_block(resp: requests.Response) -> None:
        """Turn an environment egress block into a clear, actionable error."""
        blocked = resp.status_code == 403 and (
            resp.headers.get("x-deny-reason") == "host_not_allowed"
            or "not in allowlist" in (resp.text or "").lower()
        )
        if blocked:
            raise EgressBlockedError(
                "Blocked by the environment's network policy "
                "(not by superaggregator). Add the host to this "
                "environment's network egress allowlist, then start a fresh "
                "session. See https://code.claude.com/docs/en/claude-code-on-the-web"
            )

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        resp = self._raw_request(method, path, **kwargs)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exc:
            raise SuperagrigratorError(f"{method} {path} failed: {exc}") from exc
        if not resp.content:
            return None
        return resp.json()

    # -- public API -------------------------------------------------------

    def health_check(self) -> bool:
        """Return True if superaggregator is reachable.

        Raises:
            EgressBlockedError: if the network policy blocks the host, since
                that is a configuration problem the caller must surface rather
                than silently treat as "the service is down".
        """
        try:
            self._request("GET", "/health")
            return True
        except EgressBlockedError:
            raise
        except SuperagrigratorError:
            return False

    def get_price(self, symbol: str) -> dict[str, Any]:
        """Fetch the latest aggregated price for ``symbol`` (e.g. 'BTC-USD')."""
        return self._request("GET", f"/prices/{symbol}")

    def place_order(self, order: dict[str, Any]) -> dict[str, Any]:
        """Submit an order to superaggregator for routing/execution."""
        return self._request("POST", "/orders", json=order)

    def discover(self) -> list[dict[str, Any]]:
        """Probe candidate endpoints and report which ones respond.

        Useful for mapping the real API once the host is reachable. Returns a
        list of ``{"path", "status", "content_type"}`` records. Raises
        EgressBlockedError early if the host itself is blocked.
        """
        results: list[dict[str, Any]] = []
        for path in _CANDIDATE_PATHS:
            try:
                resp = self._raw_request("GET", path)
            except EgressBlockedError:
                raise
            except SuperagrigratorError as exc:
                results.append({"path": path, "status": "error", "detail": str(exc)})
                continue
            results.append(
                {
                    "path": path,
                    "status": resp.status_code,
                    "content_type": resp.headers.get("content-type", ""),
                }
            )
        return results
