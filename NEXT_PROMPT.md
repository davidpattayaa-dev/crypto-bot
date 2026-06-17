# Next session — prompt to paste

Use this once you've added the host to the environment's network allowlist
from a computer. Copy everything in the box below into a fresh Claude Code
session for `crypto-bot`.

---

```
Continue the superaggregator integration on branch
`claude/superagrigrator-connection-xctqo1`.

Context (already done in a previous session):
- The bot is a config-driven HTTP client for https://superaggregator.fly.dev
  (an open endpoint, no login).
- Code lives in crypto_bot/ (config.py, aggregator.py, cli.py) with passing
  tests in tests/ and CI in .github/workflows/ci.yml.
- The API paths in aggregator.py (/health, /prices/{symbol}, /orders) are
  PLACEHOLDERS — they have not been verified against the real site yet,
  because the host was blocked by the environment's network allowlist.

I have now added `superaggregator.fly.dev` to the network allowlist.

Please:
1. Confirm you can reach the host: run `python -m crypto_bot.cli discover`
   and show me which endpoints respond.
2. Fetch https://superaggregator.fly.dev/chart and inspect the page plus any
   JSON/data requests it makes (look for /api/... routes). Figure out the real
   endpoints and response shapes.
3. Replace the placeholder paths and response handling in
   crypto_bot/aggregator.py with the real API. Update get_price (and add a
   chart/candles method if that's what the site serves).
4. Update the tests to match the real response shapes, and the README.
5. Run the tests, then commit and push to the branch.

If the real API differs a lot from my assumptions (e.g. it's websocket-based,
or needs query params I can't guess), stop and ask me before guessing.
```

---

## If you can't allowlist the host

Paste this instead, filling in what you see in your browser's Network tab on
`https://superaggregator.fly.dev/chart`:

```
The superaggregator chart page loads its data from this request:
  URL: <e.g. /api/chart?symbol=BTC-USD&interval=1h>
  Method: <GET/POST>
  Auth: <none / header / cookie>
  Sample response:
  <paste a snippet of the JSON here>

Wire crypto_bot/aggregator.py to this real endpoint on branch
`claude/superagrigrator-connection-xctqo1`, update the tests and README,
run the tests, and push.
```
