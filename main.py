import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config.config import config
from handlers import voice, video, audio, style
from loguru import logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger.add("bot.log", rotation="1 day", compression="zip")

async def main():
    # Initialize bot and dispatcher with new DefaultBotProperties
    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=config.BOT_TOKEN, default=default)
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(voice.router)
    dp.include_router(video.router)
    dp.include_router(audio.router)
    dp.include_router(style.router)
    
    # Start polling
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
