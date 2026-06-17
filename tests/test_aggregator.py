"""Tests for the superagrigrator client. Network is mocked via `responses`."""

import pytest
import requests
import responses

from crypto_bot.aggregator import (
    EgressBlockedError,
    SuperagrigratorClient,
    SuperagrigratorError,
)
from crypto_bot.config import Settings

BASE_URL = "https://api.superagrigrator.test"


@pytest.fixture
def client() -> SuperagrigratorClient:
    return SuperagrigratorClient(
        Settings(base_url=BASE_URL, api_key="test-key", timeout=5, backoff=0)
    )


@responses.activate
def test_health_check_ok(client: SuperagrigratorClient):
    responses.get(f"{BASE_URL}/health", json={"status": "ok"}, status=200)
    assert client.health_check() is True


@responses.activate
def test_health_check_failure(client: SuperagrigratorClient):
    responses.get(f"{BASE_URL}/health", status=503)
    assert client.health_check() is False


@responses.activate
def test_sends_auth_header_when_key_set(client: SuperagrigratorClient):
    responses.get(f"{BASE_URL}/health", json={}, status=200)
    client.health_check()
    assert responses.calls[0].request.headers["Authorization"] == "Bearer test-key"


@responses.activate
def test_no_auth_header_when_key_absent():
    # Open endpoint: no api_key -> no Authorization header sent.
    open_client = SuperagrigratorClient(Settings(base_url=BASE_URL))
    responses.get(f"{BASE_URL}/health", json={}, status=200)
    open_client.health_check()
    assert "Authorization" not in responses.calls[0].request.headers


@responses.activate
def test_get_price(client: SuperagrigratorClient):
    responses.get(
        f"{BASE_URL}/prices/BTC-USD",
        json={"symbol": "BTC-USD", "price": "65000.00"},
        status=200,
    )
    assert client.get_price("BTC-USD")["price"] == "65000.00"


@responses.activate
def test_place_order(client: SuperagrigratorClient):
    responses.post(f"{BASE_URL}/orders", json={"id": "abc", "status": "filled"}, status=201)
    result = client.place_order({"symbol": "BTC-USD", "side": "buy", "qty": 0.1})
    assert result["status"] == "filled"


@responses.activate
def test_error_is_wrapped(client: SuperagrigratorClient):
    responses.get(f"{BASE_URL}/prices/BTC-USD", status=500)
    with pytest.raises(SuperagrigratorError):
        client.get_price("BTC-USD")


@responses.activate
def test_egress_block_raises_clear_error(client: SuperagrigratorClient):
    responses.get(
        f"{BASE_URL}/health",
        status=403,
        headers={"x-deny-reason": "host_not_allowed"},
        body="Host not in allowlist",
    )
    with pytest.raises(EgressBlockedError):
        client.health_check()


@responses.activate
def test_retries_then_succeeds(client: SuperagrigratorClient):
    # First attempt is a transient connection error, second succeeds.
    responses.get(f"{BASE_URL}/health", body=requests.ConnectionError("boom"))
    responses.get(f"{BASE_URL}/health", json={"status": "ok"}, status=200)
    assert client.health_check() is True
    assert len(responses.calls) == 2


@responses.activate
def test_discover_lists_endpoints(client: SuperagrigratorClient):
    responses.get(f"{BASE_URL}/health", json={"status": "ok"}, status=200)
    # Register every other candidate path the client probes, as 404.
    for path in ("/", "/healthz", "/api", "/api/health", "/chart", "/api/chart",
                 "/prices", "/api/prices", "/candles", "/api/candles",
                 "/symbols", "/api/symbols"):
        responses.get(f"{BASE_URL}{path}", status=404)

    rows = client.discover()
    paths = {r["path"]: r["status"] for r in rows}
    assert paths["/health"] == 200
    assert paths["/chart"] == 404
