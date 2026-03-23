from __future__ import annotations

from urllib.request import Request, urlopen


DEFAULT_TIMEOUT = 20
DEFAULT_USER_AGENT = "crypto-indicators-digest/0.1 (+https://github.com/openai/codex)"


def fetch_text(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    request = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset)
