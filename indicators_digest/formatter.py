from __future__ import annotations

import re
from html import escape

from .models import IndicatorFailure, IndicatorReading


def format_digest(
    *,
    readings: list[IndicatorReading],
    failures: list[IndicatorFailure],
) -> str:
    lines = [
        "Daily crypto indicators",
        "",
    ]

    for reading in readings:
        lines.append(
            f"- <a href=\"{escape(reading.source_url, quote=True)}\">{escape(reading.name)}</a>: "
            f"{_bold_numbers(str(reading.value))} ({_bold_numbers(reading.label)})"
        )

    for failure in failures:
        lines.append(
            f"- <a href=\"{escape(failure.source_url, quote=True)}\">{escape(failure.name)}</a>: "
            f"failed to fetch ({escape(failure.error)})"
        )

    return "\n".join(lines)


_NUMBER_RE = re.compile(r"\d+(?:[./]\d+)*(?:,\d+)*(?:\.\d+)?%?")


def _bold_numbers(text: str) -> str:
    escaped_text = escape(text)
    return _NUMBER_RE.sub(lambda match: f"<b>{match.group(0)}</b>", escaped_text)
