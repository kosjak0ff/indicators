from __future__ import annotations

from datetime import datetime
from typing import Callable
from zoneinfo import ZoneInfo

from .config import Settings
from .formatter import format_digest
from .models import IndicatorFailure, IndicatorReading
from .sources import fetch_altcoin_season, fetch_fear_greed
from .telegram import send_message


Fetcher = Callable[[], IndicatorReading]


def run_once(settings: Settings) -> str:
    fetchers: list[Fetcher] = [fetch_altcoin_season, fetch_fear_greed]
    readings: list[IndicatorReading] = []
    failures: list[IndicatorFailure] = []

    for fetcher in fetchers:
        try:
            readings.append(fetcher())
        except Exception as exc:
            source_name = _source_name_for_fetcher(fetcher)
            source_url = _source_url_for_fetcher(fetcher)
            failures.append(
                IndicatorFailure(name=source_name, source_url=source_url, error=str(exc))
            )

    message = format_digest(
        readings=readings,
        failures=failures,
        now=datetime.now(tz=ZoneInfo(settings.timezone)),
        timezone_name=settings.timezone,
    )

    send_message(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
        text=message,
        message_thread_id=settings.telegram_message_thread_id,
    )

    if failures:
        raise RuntimeError("Digest sent with partial failures")

    return message


def _source_name_for_fetcher(fetcher: Fetcher) -> str:
    if fetcher is fetch_altcoin_season:
        return "Altcoin Season Index"
    if fetcher is fetch_fear_greed:
        return "Fear & Greed Index"
    return fetcher.__name__


def _source_url_for_fetcher(fetcher: Fetcher) -> str:
    if fetcher is fetch_altcoin_season:
        return "https://www.blockchaincenter.net/en/altcoin-season-index/"
    if fetcher is fetch_fear_greed:
        return "https://alternative.me/crypto/fear-and-greed-index/"
    return ""
