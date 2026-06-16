"""Tests for the superagrigrator client. Network is mocked via `responses`."""

import pytest
import responses

from crypto_bot.aggregator import SuperagrigratorClient, SuperagrigratorError
from crypto_bot.config import Settings

BASE_URL = "https://api.superagrigrator.test"


@pytest.fixture
def client() -> SuperagrigratorClient:
    return SuperagrigratorClient(
        Settings(base_url=BASE_URL, api_key="test-key", timeout=5)
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
def test_sends_auth_header(client: SuperagrigratorClient):
    responses.get(f"{BASE_URL}/health", json={}, status=200)
    client.health_check()
    assert responses.calls[0].request.headers["Authorization"] == "Bearer test-key"


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
