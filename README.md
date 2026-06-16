# crypto-bot

A small crypto bot that connects to the **superagrigrator** service (a "super
aggregator" of market data / order routing) over its HTTP API.

The connection is fully config-driven: point the bot at any superagrigrator
endpoint by setting two environment variables — no code changes required.

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure the connection (copy the example and fill in your values)
cp .env.example .env
#   SUPERAGRIGRATOR_BASE_URL=https://api.superagrigrator.example
#   SUPERAGRIGRATOR_API_KEY=your-key-here

# 3. Test that the bot can reach superagrigrator
python -m crypto_bot.cli ping
```

If the connection works you'll see:

```
✓ Connected to superagrigrator at https://api.superagrigrator.example
```

## Configuration

| Env var                      | Required | Default | Description                              |
| ---------------------------- | -------- | ------- | ---------------------------------------- |
| `SUPERAGRIGRATOR_BASE_URL`   | yes      | —       | Base URL of the superagrigrator API.     |
| `SUPERAGRIGRATOR_API_KEY`    | yes      | —       | API key used for authenticating.         |
| `SUPERAGRIGRATOR_TIMEOUT`    | no       | `10`    | Per-request timeout in seconds.          |

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
