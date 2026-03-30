from __future__ import annotations

from datetime import datetime, timezone

from .models import IndicatorFailure, IndicatorReading


def format_digest(
    *,
    readings: list[IndicatorReading],
    failures: list[IndicatorFailure],
    now: datetime,
) -> str:
    lines = [
        "Daily crypto indicators digest",
        f"Scheduled time: {now.astimezone(timezone.utc):%Y-%m-%d %H:%M %Z}",
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
