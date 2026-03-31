from __future__ import annotations

import json
from pathlib import Path

from .models import IndicatorReading


_OVERRIDE_SPECS = {
    "altcoin_season": (
        "Altcoin Season Index",
        "https://www.blockchaincenter.net/en/altcoin-season-index/",
    ),
    "fear_greed": (
        "Fear & Greed Index",
        "https://alternative.me/crypto/fear-and-greed-index/",
    ),
    "bull_market_peak": (
        "Bull Market Peak Signals",
        "https://www.coinglass.com/bull-market-peak-signals",
    ),
}


def load_manual_readings(path: str | Path) -> dict[str, IndicatorReading]:
    raw = Path(path).read_text(encoding="utf-8")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Manual indicators file is not valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("Manual indicators file must contain a JSON object")

    readings: dict[str, IndicatorReading] = {}
    for key, spec in _OVERRIDE_SPECS.items():
        item = payload.get(key)
        if item is None:
            continue
        if not isinstance(item, dict):
            raise ValueError(f"Manual indicator {key!r} must be a JSON object")

        value = item.get("value")
        label = item.get("label")
        if value is None:
            raise ValueError(f"Manual indicator {key!r} is missing 'value'")
        if label is None:
            raise ValueError(f"Manual indicator {key!r} is missing 'label'")
        if not isinstance(label, str):
            raise ValueError(f"Manual indicator {key!r} field 'label' must be a string")
        if not isinstance(value, (int, str)):
            raise ValueError(
                f"Manual indicator {key!r} field 'value' must be a string or integer"
            )

        name, source_url = spec
        readings[key] = IndicatorReading(
            name=name,
            value=value,
            label=label.strip(),
            source_url=source_url,
        )

    return readings
