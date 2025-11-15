from typing import List

from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


def _parse_unlimited_users(value: str | None) -> List[str]:
    if not value:
        return []
    return [user.strip() for user in value.split(',') if user.strip()]

class Config(BaseModel):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY")
    ADMIN_USER_ID: int = int(os.getenv("ADMIN_USER_ID", "0"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "5"))
    UNLIMITED_USERS_FILE: str = os.getenv("UNLIMITED_USERS_FILE", "data/unlimited_users.json")
    UNLIMITED_USERS: List[str] = _parse_unlimited_users(os.getenv("UNLIMITED_USERS"))

config = Config()
