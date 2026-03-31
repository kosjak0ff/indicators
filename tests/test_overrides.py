from pathlib import Path

from indicators_digest.overrides import load_manual_readings


def test_load_manual_readings_parses_known_indicators(tmp_path: Path) -> None:
    payload = """
    {
      "altcoin_season": {
        "value": 55,
        "label": "not Altcoin Season"
      },
      "bull_market_peak": {
        "value": "Hit 0/30",
        "label": "Average Progress 33.93%, Hold 100%"
      }
    }
    """
    path = tmp_path / "manual-indicators.json"
    path.write_text(payload, encoding="utf-8")

    readings = load_manual_readings(path)

    assert readings["altcoin_season"].value == 55
    assert readings["altcoin_season"].label == "not Altcoin Season"
    assert readings["bull_market_peak"].value == "Hit 0/30"
    assert readings["bull_market_peak"].label == "Average Progress 33.93%, Hold 100%"
