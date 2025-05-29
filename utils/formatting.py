from models.transcription import TranscriptionResult
from handlers.style import get_style_keyboard
from aiogram.types import InlineKeyboardMarkup
from typing import List, Tuple, Optional

def split_long_message(text: str, limit: int = 4000) -> List[str]:
    """Split long message into parts that fit Telegram message limit."""
    if len(text) <= limit:
        return [text]
    
    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        
        # Find the last space before limit
        split_index = text.rfind(' ', 0, limit)
        if split_index == -1:
            split_index = limit
        
        parts.append(text[:split_index])
        text = text[split_index:].lstrip()
    
    return parts

def format_transcription(result: TranscriptionResult) -> Tuple[List[str], Optional[InlineKeyboardMarkup]]:
    """Format transcription result into parts of messages with style buttons in the last one."""
    # Split text into parts if needed
    parts = split_long_message(result.text)
    
    # Return parts and keyboard for the last message
    return parts, get_style_keyboard()
