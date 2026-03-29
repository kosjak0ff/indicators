# Crypto Indicators Digest

Small Python script that fetches crypto market indicators and sends a daily summary into a Telegram chat thread.

## Sources

- Altcoin Season Index: `https://www.blockchaincenter.net/en/altcoin-season-index/`
- Fear & Greed Index: `https://alternative.me/crypto/fear-and-greed-index/`
- Bull Market Peak Signals: `https://www.coinglass.com/bull-market-peak-signals`

## What it does

- fetches all configured indicators on demand
- formats a single Telegram message
- posts to a configured chat and forum topic
- supports a DST-aware local timezone via `TIMEZONE`

## Configuration

Copy `.env.example` to `.env` and fill in the values:

```env
TIMEZONE=Europe/Riga
SUMMARY_HOUR=6
SUMMARY_MINUTE=0
TELEGRAM_BOT_TOKEN=123456:replace-me
TELEGRAM_CHAT_ID=-1001234567890
TELEGRAM_MESSAGE_THREAD_ID=42
```

`TIMEZONE` should be an IANA timezone name such as `Europe/Riga`, `Europe/Berlin`, or `Europe/Vilnius`.

## Local run

Create a virtual environment and install test dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
```

The CoinGlass source renders its values client-side, so local runs also require `node` and `google-chrome-stable` to be available on the machine.

Run the digest manually:

```bash
PYTHONPATH=. python main.py run
```

Print raw Telegram updates to discover identifiers:

```bash
PYTHONPATH=. python main.py telegram-updates
```

Or use the helper:

```bash
PYTHONPATH=. python scripts/get_telegram_ids.py
```

## How to get Telegram IDs

1. Create a bot via `@BotFather` and copy the token into `.env`.
2. Add the bot to your target group or supergroup.
3. If you use forum topics, send a test message in the exact topic you want to use.
4. Run `PYTHONPATH=. python main.py telegram-updates`.
5. Inspect the output fields:
   - `chat_id` is your Telegram chat identifier.
   - `message_thread_id` is the forum topic identifier.

## Ubuntu VPS setup

Example setup:

```bash
sudo apt update
sudo apt install -y python3 python3-venv
git clone <your-repo-url>
cd indicators
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Edit `.env`, then test the script:

```bash
PYTHONPATH=. .venv/bin/python main.py run
```

## Daily schedule at 06:00 local time with DST

Use `CRON_TZ` with the same timezone you store in `.env`.

Example crontab:

```cron
CRON_TZ=Europe/Riga
0 6 * * * cd /path/to/indicators && PYTHONPATH=. .venv/bin/python main.py run >> /var/log/indicators.log 2>&1
```

This keeps the run pinned to 06:00 local time even when DST changes.
