from __future__ import annotations

from datetime import datetime, timezone
from typing import Callable

from .config import Settings
from .formatter import format_digest
from .models import IndicatorFailure, IndicatorReading
from .sources import (
    fetch_altcoin_season,
    fetch_coinglass_bull_market_peak,
    fetch_fear_greed,
)
from .telegram import send_message


Fetcher = Callable[[], IndicatorReading]


def run_once(
    settings: Settings,
    *,
    manual_readings: dict[str, IndicatorReading] | None = None,
) -> str:
    sources: list[tuple[str, Fetcher]] = [
        ("altcoin_season", fetch_altcoin_season),
        ("fear_greed", fetch_fear_greed),
        ("bull_market_peak", fetch_coinglass_bull_market_peak),
    ]
    readings: list[IndicatorReading] = []
    failures: list[IndicatorFailure] = []
    manual_readings = manual_readings or {}

    for source_key, fetcher in sources:
        manual_reading = manual_readings.get(source_key)
        if manual_reading is not None:
            readings.append(manual_reading)
            continue
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
    if fetcher is fetch_coinglass_bull_market_peak:
        return "Bull Market Peak Signals"
    return fetcher.__name__


def _source_url_for_fetcher(fetcher: Fetcher) -> str:
    if fetcher is fetch_altcoin_season:
        return "https://www.blockchaincenter.net/en/altcoin-season-index/"
    if fetcher is fetch_fear_greed:
        return "https://alternative.me/crypto/fear-and-greed-index/"
    if fetcher is fetch_coinglass_bull_market_peak:
        return "https://www.coinglass.com/bull-market-peak-signals"
    return ""
