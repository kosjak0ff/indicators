from __future__ import annotations

import json
import re

from .http import fetch_text
from .models import IndicatorReading


ALTCOIN_SEASON_URL = "https://www.blockchaincenter.net/en/altcoin-season-index/"
FEAR_GREED_URL = "https://alternative.me/crypto/fear-and-greed-index/"
FEAR_GREED_API_URL = "https://api.alternative.me/fng/"

_ALTCOIN_VALUE_RE = re.compile(
    r'Altcoin Season\s*\((?:<!-- -->)?(?P<value>\d+)(?:<!-- -->)?\)'
)
_ALTCOIN_LABEL_RE = re.compile(r"<span>It is (?P<label>[^<]+)</span>")


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
