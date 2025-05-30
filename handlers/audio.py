from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from services.deepgram import DeepgramService
from utils.formatting import format_transcription
from utils.telegram_formatting import (
    format_transcription_header, format_error_message
)
from config.config import config
from loguru import logger
import traceback

router = Router()
deepgram_service = DeepgramService(config.DEEPGRAM_API_KEY)

@router.message(F.audio)
async def handle_audio(message: Message):
    try:
        # Use typing indicator during processing
        async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
            # Get file
            file = await message.bot.get_file(message.audio.file_id)
            file_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"
            
            logger.debug(f"Processing audio file. File URL: {file_url}")
            
            # Transcribe
            result = await deepgram_service.transcribe_audio(file_url)
        
        # Format with header
        header = format_transcription_header(result.confidence)
        parts, reply_markup = format_transcription(result)
        
        # Send header with first part
        if parts:
            await message.answer(header)
            await message.answer(parts[0], reply_markup=reply_markup if len(parts) == 1 else None)
            
            # Send remaining parts
            for i, part in enumerate(parts[1:], 1):
                is_last = i == len(parts) - 1
                await message.answer(part, reply_markup=reply_markup if is_last else None)
        else:
            await message.answer(header)
        
    except Exception as e:
        logger.error(f"Full error: {str(e)}\n{traceback.format_exc()}")
        await message.answer(format_error_message(str(e)))
