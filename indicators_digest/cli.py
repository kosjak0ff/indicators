from __future__ import annotations

import argparse
import json
import sys

from .app import run_once
from .config import Settings, get_bot_token_from_env, load_dotenv
from .telegram import get_updates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Send a daily crypto indicators digest to Telegram."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run", help="Fetch indicators and send the digest to Telegram.")
    subparsers.add_parser(
        "telegram-updates",
        help="Print raw Telegram updates to help discover chat and thread identifiers.",
    )

    args = parser.parse_args(argv)
    load_dotenv()

    try:
        if args.command == "run":
            settings = Settings.from_env()
            message = run_once(settings)
            print(message)
            return 0

        if args.command == "telegram-updates":
            updates = get_updates(bot_token=get_bot_token_from_env())
            print(json.dumps(updates, indent=2))
            return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    sys.exit(main())
