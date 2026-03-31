from indicators_digest import app
from indicators_digest.models import IndicatorReading


class _Settings:
    telegram_bot_token = "bot-token"
    telegram_chat_id = "chat-id"
    telegram_message_thread_id = 42


def test_run_once_uses_manual_readings_instead_of_fetching(monkeypatch) -> None:
    sent: dict[str, str] = {}

    def fake_altcoin() -> IndicatorReading:
        return IndicatorReading(
            name="Altcoin Season Index",
            value=55,
            label="not Altcoin Season",
            source_url="https://www.blockchaincenter.net/en/altcoin-season-index/",
        )

    def fake_fear_greed() -> IndicatorReading:
        return IndicatorReading(
            name="Fear & Greed Index",
            value=11,
            label="Extreme Fear",
            source_url="https://alternative.me/crypto/fear-and-greed-index/",
        )

    def fake_send_message(
        *,
        bot_token: str,
        chat_id: str,
        text: str,
        message_thread_id: int | None = None,
    ) -> None:
        sent["bot_token"] = bot_token
        sent["chat_id"] = chat_id
        sent["text"] = text
        sent["message_thread_id"] = str(message_thread_id)

    monkeypatch.setattr(app, "fetch_altcoin_season", fake_altcoin)
    monkeypatch.setattr(app, "fetch_fear_greed", fake_fear_greed)
    monkeypatch.setattr(
        app,
        "fetch_coinglass_bull_market_peak",
        lambda: (_ for _ in ()).throw(AssertionError("manual override should skip fetch")),
    )
    monkeypatch.setattr(app, "send_message", fake_send_message)

    message = app.run_once(
        _Settings(),
        manual_readings={
            "bull_market_peak": IndicatorReading(
                name="Bull Market Peak Signals",
                value="Hit 0/30",
                label="Average Progress 33.93%, Hold 100%",
                source_url="https://www.coinglass.com/bull-market-peak-signals",
            )
        },
    )

    assert "Bull Market Peak Signals" in message
    assert "failed to fetch" not in message
    assert sent["bot_token"] == "bot-token"
    assert sent["chat_id"] == "chat-id"
    assert sent["message_thread_id"] == "42"
