from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def load_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


@dataclass(frozen=True)
class Settings:
    timezone: str
    summary_hour: int
    summary_minute: int
    telegram_bot_token: str
    telegram_chat_id: str
    telegram_message_thread_id: int | None

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        timezone = _required("TIMEZONE")
        summary_hour = int(os.getenv("SUMMARY_HOUR", "6"))
        summary_minute = int(os.getenv("SUMMARY_MINUTE", "0"))
        if not 0 <= summary_hour <= 23:
            raise ValueError("SUMMARY_HOUR must be between 0 and 23")
        if not 0 <= summary_minute <= 59:
            raise ValueError("SUMMARY_MINUTE must be between 0 and 59")

        thread_id_raw = os.getenv("TELEGRAM_MESSAGE_THREAD_ID")
        return cls(
            timezone=timezone,
            summary_hour=summary_hour,
            summary_minute=summary_minute,
            telegram_bot_token=_required("TELEGRAM_BOT_TOKEN"),
            telegram_chat_id=_required("TELEGRAM_CHAT_ID"),
            telegram_message_thread_id=int(thread_id_raw) if thread_id_raw else None,
        )


def get_bot_token_from_env() -> str:
    load_dotenv()
    return _required("TELEGRAM_BOT_TOKEN")


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value
