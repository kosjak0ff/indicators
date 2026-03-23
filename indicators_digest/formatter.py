from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from .models import IndicatorFailure, IndicatorReading


def format_digest(
    *,
    readings: list[IndicatorReading],
    failures: list[IndicatorFailure],
    now: datetime,
    timezone_name: str,
) -> str:
    local_now = now.astimezone(ZoneInfo(timezone_name))

    lines = [
        "Daily crypto indicators digest",
        f"Scheduled time: {local_now:%Y-%m-%d %H:%M %Z}",
        "",
    ]

    for reading in readings:
        lines.append(f"- {reading.name}: {reading.value} ({reading.label})")

    for failure in failures:
        lines.append(f"- {failure.name}: failed to fetch ({failure.error})")

    lines.extend(["", "Sources:"])
    for reading in readings:
        lines.append(f"- {reading.name}: {reading.source_url}")
    for failure in failures:
        lines.append(f"- {failure.name}: {failure.source_url}")

    return "\n".join(lines)
