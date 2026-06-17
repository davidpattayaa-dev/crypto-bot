# crypto-bot

A small crypto bot that connects to the **superagrigrator** service (a "super
aggregator" of market data / order routing) over its HTTP API.

The connection is fully config-driven: point the bot at any superagrigrator
endpoint by setting two environment variables — no code changes required.

The default instance is **open (no login required)**, so the bot works with
zero configuration.

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test that the bot can reach superaggregator (no config needed)
python -m crypto_bot.cli ping
```

If the connection works you'll see:

```
✓ Connected to superaggregator at https://superaggregator.fly.dev
```

## Configuration

No configuration is required for the public instance. Override only if needed:

| Env var                      | Required | Default                          | Description                          |
| ---------------------------- | -------- | -------------------------------- | ------------------------------------ |
| `SUPERAGRIGRATOR_BASE_URL`   | no       | `https://superaggregator.fly.dev`| Base URL of the superaggregator API. |
| `SUPERAGRIGRATOR_API_KEY`    | no       | _(none)_                         | Only sent if the instance needs auth.|
| `SUPERAGRIGRATOR_TIMEOUT`    | no       | `10`                             | Per-request timeout in seconds.      |

Configuration is read from the environment (and from a `.env` file if present).

## CLI

```bash
python -m crypto_bot.cli ping              # health-check the connection
python -m crypto_bot.cli price BTC-USD     # fetch a price from the aggregator
```

## Using it from code

```python
from crypto_bot.config import Settings
from crypto_bot.aggregator import SuperagrigratorClient

client = SuperagrigratorClient(Settings.from_env())

if client.health_check():
    print(client.get_price("BTC-USD"))
```

## Notes on the API surface

The exact superagrigrator endpoints (`/health`, `/prices/{symbol}`, `/orders`)
are isolated in `crypto_bot/aggregator.py`. If the real service uses different
paths or auth, that's the only file you need to adjust.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
