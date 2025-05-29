"""Telegram message formatting utilities."""
from aiogram.utils.formatting import (
    Text, Bold, Italic, Underline, Code, Pre, 
    BlockQuote, Link, TextLink, HashTag, Spoiler,
    as_list, as_section, as_key_value, as_marked_section
)
from aiogram.enums import ParseMode
import re


def escape_html(text: str) -> str:
    """Escape special HTML characters."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_transcription_header(confidence: float) -> Text:
    """Format transcription header with confidence."""
    return Text(
        Bold("📝 Транскрипция"),
        "\n",
        Italic(f"Уверенность: {confidence:.1%}"),
        "\n\n"
    )


def format_style_result(style: str, text: str) -> Text:
    """Format styled text result with proper headers."""
    style_names = {
        "proofread": "✍️ Отредактированный текст",
        "my": "⚡ Неформальный стиль",
        "business": "👔 Деловой стиль",
        "brief": "📋 Бриф"
    }
    
    header = style_names.get(style, "📄 Обработанный текст")
    
    # For brief style, parse the sections and format them
    if style == "brief":
        return format_brief_sections(text)
    
    return Text(
        Bold(header),
        "\n\n",
        text
    )


def format_brief_sections(text: str) -> Text:
    """Format brief sections with proper styling."""
    sections = []
    
    # Split text into lines
    lines = text.split('\n')
    current_section = []
    
    for line in lines:
        line = line.strip()
        
        # Check if it's a header (starts with emoji or specific keywords)
        if (line.startswith('📝') or line.startswith('Что делаем:') or 
            line.startswith('Зачем:') or line.startswith('Как:') or 
            line.startswith('Сроки:') or line.startswith('Вопросы:')):
            
            # Save previous section if exists
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []
            
            # Add formatted header
            if line.startswith('📝'):
                sections.append(Bold(line))
            else:
                sections.append(Bold(line))
        else:
            # Add regular line
            if line:
                current_section.append(line)
    
    # Add last section
    if current_section:
        sections.append('\n'.join(current_section))
    
    # Join all sections with double newline
    return Text(*[
        item if isinstance(item, (Bold, Italic, Text)) else Text(item)
        for item in sections
    ], sep="\n\n")


def format_error_message(error: str) -> Text:
    """Format error message."""
    return Text(
        Bold("❌ Ошибка"),
        "\n",
        Code(error)
    )


def format_processing_message() -> Text:
    """Format processing status message."""
    return Text(
        Italic("⏳ Обрабатываю...")
    )