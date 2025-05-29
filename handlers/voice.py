from aiogram import Router, F
from aiogram.types import Message
from services.deepgram import DeepgramService
from utils.formatting import format_transcription
from config.config import config
from loguru import logger
import traceback

router = Router()
deepgram_service = DeepgramService(config.DEEPGRAM_API_KEY)

@router.message(F.voice)
async def handle_voice(message: Message):
    try:
        # Show processing status
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        # Get file
        file = await message.bot.get_file(message.voice.file_id)
        file_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"
        
        logger.debug(f"Processing voice message. File URL: {file_url}")
        
        # Transcribe
        result = await deepgram_service.transcribe_audio(file_url)
        
        # Format and send
        parts, reply_markup = format_transcription(result)
        
        # Send all parts except last one
        for part in parts[:-1]:
            await message.answer(part)
        
        # Send last part with keyboard
        await message.answer(parts[-1], reply_markup=reply_markup)
        
    except Exception as e:
        error_msg = f"Ошибка: {str(e)}"
        logger.error(f"Error processing voice message: {str(e)}\n{traceback.format_exc()}")
        await message.answer(error_msg)
