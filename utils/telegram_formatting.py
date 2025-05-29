"""Telegram message formatting utilities."""
import html


def escape_html(text: str) -> str:
    """Escape special HTML characters."""
    return html.escape(text)


def format_transcription_header(confidence: float) -> str:
    """Format transcription header with confidence."""
    return f"📝 <b>Транскрипция</b>\n<i>Уверенность: {confidence:.1%}</i>\n\n"


def format_style_result(style: str, text: str) -> str:
    """Format styled text result without headers for clean copy-paste."""
    # Return just the processed text without any headers
    # User wants clean text they can copy-paste without editing
    return text




def format_error_message(error: str) -> str:
    """Format error message."""
    escaped_error = escape_html(error)
    return f"❌ <b>Ошибка</b>\n<code>{escaped_error}</code>"
