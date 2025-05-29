from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from services.anthropic import AnthropicService
from config.config import config
from loguru import logger

router = Router()
anthropic_service = AnthropicService(config.ANTHROPIC_API_KEY)

def get_style_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with style buttons."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✍️ Proofread", callback_data="style_proofread"),
                InlineKeyboardButton(text="⚡ Informal", callback_data="style_my"),
                InlineKeyboardButton(text="👔 Business", callback_data="style_business")
            ],
            [
                InlineKeyboardButton(text="📋 Brief", callback_data="style_brief")
            ]
        ]
    )

@router.callback_query(F.data.startswith("style_"))
async def process_style_selection(callback: CallbackQuery):
    """Handle style selection."""
    try:
        # Show that we're processing the callback
        await callback.answer("Обрабатываю...")
        
        # Get original text from the message (now it's clean, without prefix)
        original_text = callback.message.text
        
        # Get selected style
        style = callback.data.replace("style_", "")
        
        logger.debug(f"Processing text with style {style}. Text length: {len(original_text)}")
        
        # Process text with selected style
        processed_text = await anthropic_service.process_text(original_text, style)
        
        # Send result as a new message (without prefix)
        await callback.message.answer(processed_text)
        
    except Exception as e:
        error_msg = f"Ошибка: {str(e)}"
        logger.error(f"Error processing text: {str(e)}")
        await callback.message.answer(error_msg) 
