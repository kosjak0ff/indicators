from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def send_message(
    *,
    bot_token: str,
    chat_id: str,
    text: str,
    message_thread_id: int | None = None,
) -> dict:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    if message_thread_id is not None:
        payload["message_thread_id"] = message_thread_id

    return _telegram_request(bot_token, "sendMessage", payload)


def get_updates(*, bot_token: str, offset: int | None = None) -> dict:
    payload: dict[str, int] = {}
    if offset is not None:
        payload["offset"] = offset
    return _telegram_request(bot_token, "getUpdates", payload)


def _telegram_request(bot_token: str, method: str, payload: dict) -> dict:
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    data = urlencode(payload).encode("utf-8")
    request = Request(url, data=data)
    with urlopen(request, timeout=20) as response:
        body = response.read().decode(response.headers.get_content_charset() or "utf-8")
    parsed = json.loads(body)
    if not parsed.get("ok"):
        raise ValueError(f"Telegram API error: {parsed}")
    return parsed
