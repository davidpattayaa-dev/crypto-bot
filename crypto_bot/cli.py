"""Command-line entry point for the crypto-bot superaggregator connection.

Usage:
    python -m crypto_bot.cli ping
    python -m crypto_bot.cli price BTC-USD
    python -m crypto_bot.cli discover
"""

from __future__ import annotations

import argparse
import json
import sys

from .aggregator import (
    EgressBlockedError,
    SuperagrigratorClient,
    SuperagrigratorError,
)
from .config import ConfigError, Settings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crypto-bot",
        description="Connect to and query the superaggregator service.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("ping", help="Health-check the superaggregator connection.")

    price = sub.add_parser("price", help="Fetch an aggregated price.")
    price.add_argument("symbol", help="Trading pair, e.g. BTC-USD")

    sub.add_parser(
        "discover",
        help="Probe common endpoints and report which ones respond.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 2

    client = SuperagrigratorClient(settings)

    try:
        if args.command == "ping":
            if client.health_check():
                print(f"✓ Connected to superaggregator at {settings.base_url}")
                return 0
            print(
                f"✗ Could not reach superaggregator at {settings.base_url}",
                file=sys.stderr,
            )
            return 1

        if args.command == "price":
            print(json.dumps(client.get_price(args.symbol), indent=2))
            return 0

        if args.command == "discover":
            print(f"Probing {settings.base_url} ...")
            for row in client.discover():
                status = row.get("status")
                extra = row.get("content_type") or row.get("detail", "")
                print(f"  {str(status):>6}  {row['path']:<14} {extra}")
            return 0

    except EgressBlockedError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 3
    except SuperagrigratorError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
