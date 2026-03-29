from indicators_digest.sources import (
    parse_altcoin_season_html,
    parse_coinglass_bull_market_peak_text,
    parse_fear_greed_payload,
)


def test_parse_altcoin_season_html_extracts_value_and_label() -> None:
    html = """
    <button class="btn btn-primary" type="button">Altcoin Season (<!-- -->55<!-- -->)</button>
    <div><span>It is not Altcoin Season!</span></div>
    """

    reading = parse_altcoin_season_html(html)

    assert reading.name == "Altcoin Season Index"
    assert reading.value == 55
    assert reading.label == "not Altcoin Season"


def test_parse_fear_greed_payload_extracts_current_entry() -> None:
    payload = """
    {
      "name": "Fear and Greed Index",
      "data": [
        {
          "value": "8",
          "value_classification": "Extreme Fear",
          "timestamp": "1774224000"
        }
      ]
    }
    """

    reading = parse_fear_greed_payload(payload)

    assert reading.name == "Fear & Greed Index"
    assert reading.value == 8
    assert reading.label == "Extreme Fear"


def test_parse_coinglass_bull_market_peak_text_extracts_requested_metrics() -> None:
    text = """
    Bull Market Peak Indicators - Sell At The Top
    Update Time: 2026-03-29 19:21
    Hit : 0/30
    Average Progress : 33.93%
    Hold 100%
    0% Sell
    """

    reading = parse_coinglass_bull_market_peak_text(text)

    assert reading.name == "Bull Market Peak Signals"
    assert reading.value == "Hit 0/30"
    assert reading.label == "Average Progress 33.93%, Hold 100%"
