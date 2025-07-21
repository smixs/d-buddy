from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Config(BaseModel):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY")
    ADMIN_USER_ID: int = int(os.getenv("ADMIN_USER_ID", "0"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "5"))

config = Config()
