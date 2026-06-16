"""Command-line entry point for the crypto-bot superagrigrator connection.

Usage:
    python -m crypto_bot.cli ping
    python -m crypto_bot.cli price BTC-USD
"""

from __future__ import annotations

import argparse
import json
import sys

from .aggregator import SuperagrigratorClient, SuperagrigratorError
from .config import ConfigError, Settings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crypto-bot",
        description="Connect to and query the superagrigrator service.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ping", help="Health-check the superagrigrator connection.")

    price = sub.add_parser("price", help="Fetch an aggregated price.")
    price.add_argument("symbol", help="Trading pair, e.g. BTC-USD")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 2

    client = SuperagrigratorClient(settings)

    if args.command == "ping":
        if client.health_check():
            print(f"✓ Connected to superagrigrator at {settings.base_url}")
            return 0
        print(
            f"✗ Could not reach superagrigrator at {settings.base_url}",
            file=sys.stderr,
        )
        return 1

    if args.command == "price":
        try:
            data = client.get_price(args.symbol)
        except SuperagrigratorError as exc:
            print(f"✗ {exc}", file=sys.stderr)
            return 1
        print(json.dumps(data, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
