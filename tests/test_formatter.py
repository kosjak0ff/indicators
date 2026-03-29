from datetime import datetime, timezone

from indicators_digest.formatter import format_digest
from indicators_digest.models import IndicatorFailure, IndicatorReading


def test_format_digest_lists_readings_and_failures() -> None:
    message = format_digest(
        readings=[
            IndicatorReading(
                name="Altcoin Season Index",
                value=55,
                label="not Altcoin Season",
                source_url="https://example.com/altcoin",
            ),
            IndicatorReading(
                name="Bull Market Peak Signals",
                value="Hit 0/30",
                label="Average Progress 33.93%, Hold 100%",
                source_url="https://example.com/bmps",
            ),
        ],
        failures=[
            IndicatorFailure(
                name="Fear & Greed Index",
                source_url="https://example.com/fng",
                error="timeout",
            )
        ],
        now=datetime(2026, 3, 23, 4, 0, tzinfo=timezone.utc),
        timezone_name="Europe/Riga",
    )

    assert "Scheduled time: 2026-03-23 06:00 EET" in message
    assert "- Altcoin Season Index: 55 (not Altcoin Season)" in message
    assert (
        "- Bull Market Peak Signals: Hit 0/30 (Average Progress 33.93%, Hold 100%)"
        in message
    )
    assert "- Fear & Greed Index: failed to fetch (timeout)" in message
