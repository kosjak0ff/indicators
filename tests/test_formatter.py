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
    )

    assert "Daily crypto indicators" in message
    assert "Scheduled time:" not in message
    assert (
        '- <a href="https://example.com/altcoin">Altcoin Season Index</a>: '
        "<b>55</b> (not Altcoin Season)" in message
    )
    assert (
        '- <a href="https://example.com/bmps">Bull Market Peak Signals</a>: '
        'Hit <b>0/30</b> (Average Progress <b>33.93%</b>, Hold <b>100%</b>)'
        in message
    )
    assert (
        '- <a href="https://example.com/fng">Fear &amp; Greed Index</a>: '
        "failed to fetch (timeout)" in message
    )
