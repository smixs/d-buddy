"""Telegram message formatting utilities."""
import html


def escape_html(text: str) -> str:
    """Escape special HTML characters."""
    return html.escape(text)


def format_transcription_header(confidence: float) -> str:
    """Format transcription header with confidence."""
    return f"📝 <b>Транскрипция</b>\n<i>Уверенность: {confidence:.1%}</i>\n\n"


def format_style_result(style: str, text: str) -> str:
    """Format styled text result with proper headers."""
    style_names = {
        "proofread": "✍️ <b>Отредактированный текст</b>",
        "my": "⚡ <b>Неформальный стиль</b>",
        "business": "👔 <b>Деловой стиль</b>",
        "brief": "📋 <b>Обработанный текст</b>"
    }
    
    header = style_names.get(style, "📄 <b>Обработанный текст</b>")
    
    return f"{header}\n\n{text}"




def format_error_message(error: str) -> str:
    """Format error message."""
    escaped_error = escape_html(error)
    return f"❌ <b>Ошибка</b>\n<code>{escaped_error}</code>"


def format_processing_message() -> str:
    """Format processing status message."""
    return "<i>⏳ Обрабатываю...</i>"