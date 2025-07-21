from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from services.anthropic import AnthropicService
from services.metrics import MetricsService
from models.metrics import MetricsEvent
from utils.telegram_formatting import format_style_result, format_error_message
from config.config import config
from loguru import logger

router = Router()
anthropic_service = AnthropicService(config.ANTHROPIC_API_KEY)
metrics_service = MetricsService()

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
        
        # Track metrics
        metrics_service.track_event(MetricsEvent(
            user_id=str(callback.from_user.id),
            event_type="llm_call",
            event_subtype=style
        ))
        
        # Format and send result
        formatted_result = format_style_result(style, processed_text)
        await callback.message.answer(formatted_result)
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        await callback.message.answer(format_error_message(str(e))) 
