from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from indicators_digest.config import get_bot_token_from_env
from indicators_digest.telegram import get_updates


def main() -> int:
    updates = get_updates(bot_token=get_bot_token_from_env())
    for item in updates.get("result", []):
        message = item.get("message") or item.get("channel_post") or {}
        chat = message.get("chat") or {}
        print(
            json.dumps(
                {
                    "update_id": item.get("update_id"),
                    "chat_title": chat.get("title") or chat.get("username"),
                    "chat_id": chat.get("id"),
                    "message_thread_id": message.get("message_thread_id"),
                    "text": message.get("text"),
                },
                ensure_ascii=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
