from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from .http import fetch_text
from .models import IndicatorReading


ALTCOIN_SEASON_URL = "https://www.blockchaincenter.net/en/altcoin-season-index/"
FEAR_GREED_URL = "https://alternative.me/crypto/fear-and-greed-index/"
FEAR_GREED_API_URL = "https://api.alternative.me/fng/"
COINGLASS_BULL_MARKET_PEAK_URL = "https://www.coinglass.com/bull-market-peak-signals"

_ALTCOIN_VALUE_RE = re.compile(
    r'Altcoin Season\s*\((?:<!-- -->)?(?P<value>\d+)(?:<!-- -->)?\)'
)
_ALTCOIN_LABEL_RE = re.compile(r"<span>It is (?P<label>[^<]+)</span>")
_COINGLASS_HIT_RE = re.compile(r"Hit\s*:\s*(?P<hit>\d+/\d+)")
_COINGLASS_AVG_RE = re.compile(
    r"Average Progress\s*:\s*(?P<progress>\d+(?:\.\d+)?)%"
)
_COINGLASS_HOLD_RE = re.compile(r"Hold\s+(?P<hold>\d+(?:\.\d+)?)%")
_COINGLASS_SELL_RE = re.compile(r"(?P<sell>\d+(?:\.\d+)?)%\s+Sell")


def fetch_altcoin_season() -> IndicatorReading:
    html = fetch_text(ALTCOIN_SEASON_URL)
    return parse_altcoin_season_html(html)


def parse_altcoin_season_html(html: str) -> IndicatorReading:
    value_match = _ALTCOIN_VALUE_RE.search(html)
    if not value_match:
        raise ValueError("Could not parse Altcoin Season Index value")

    label_match = _ALTCOIN_LABEL_RE.search(html)
    if not label_match:
        raise ValueError("Could not parse Altcoin Season Index label")

    label = label_match.group("label").strip().rstrip("!")
    return IndicatorReading(
        name="Altcoin Season Index",
        value=int(value_match.group("value")),
        label=label,
        source_url=ALTCOIN_SEASON_URL,
    )


def fetch_fear_greed() -> IndicatorReading:
    payload = fetch_text(FEAR_GREED_API_URL)
    return parse_fear_greed_payload(payload)


def fetch_coinglass_bull_market_peak() -> IndicatorReading:
    page_text = render_page_text(COINGLASS_BULL_MARKET_PEAK_URL)
    return parse_coinglass_bull_market_peak_text(page_text)


def parse_fear_greed_payload(payload: str) -> IndicatorReading:
    data = json.loads(payload)
    entries = data.get("data") or []
    if not entries:
        raise ValueError("Fear & Greed API returned no data")

    current = entries[0]
    return IndicatorReading(
        name="Fear & Greed Index",
        value=int(current["value"]),
        label=str(current["value_classification"]).strip(),
        source_url=FEAR_GREED_URL,
    )


def render_page_text(url: str) -> str:
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "render_page_text.js"

    try:
        result = subprocess.run(
            ["node", str(script_path), url],
            check=True,
            capture_output=True,
            text=True,
            timeout=40,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Node.js is required to render the CoinGlass page") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Timed out while rendering the CoinGlass page") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() or exc.stdout.strip() or "unknown error"
        raise RuntimeError(f"Could not render the CoinGlass page: {stderr}") from exc

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError("CoinGlass renderer returned invalid JSON") from exc

    text = str(payload.get("text") or "").strip()
    if not text:
        raise RuntimeError("CoinGlass renderer returned empty page text")
    return text


def parse_coinglass_bull_market_peak_text(text: str) -> IndicatorReading:
    hit_match = _COINGLASS_HIT_RE.search(text)
    avg_match = _COINGLASS_AVG_RE.search(text)
    hold_match = _COINGLASS_HOLD_RE.search(text)
    sell_match = _COINGLASS_SELL_RE.search(text)

    if not hit_match:
        raise ValueError("Could not parse CoinGlass bull market peak hit value")
    if not avg_match:
        raise ValueError("Could not parse CoinGlass bull market peak average progress")
    if not hold_match and not sell_match:
        raise ValueError("Could not parse CoinGlass bull market peak hold/sell value")

    hit = hit_match.group("hit")
    avg_progress = f"{avg_match.group('progress')}%"
    allocation_label = (
        f"Hold {hold_match.group('hold')}%"
        if hold_match
        else f"Sell {sell_match.group('sell')}%"
    )

    return IndicatorReading(
        name="Bull Market Peak Signals",
        value=f"Hit {hit}",
        label=f"Average Progress {avg_progress}, {allocation_label}",
        source_url=COINGLASS_BULL_MARKET_PEAK_URL,
    )
