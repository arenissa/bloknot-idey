"""Настройки читаются из .env рядом с этим файлом."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Config:
    bot_token: str
    database_path: Path


def load_config() -> Config:
    load_dotenv(BASE_DIR / ".env")
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or token == "your_bot_token_here":
        raise ValueError("Укажите BOT_TOKEN в файле .env (см. .env.example).")
    return Config(bot_token=token, database_path=BASE_DIR / "data" / "tasks.sqlite3")
