from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from services.metrics import MetricsService
from config.config import config
from loguru import logger
from datetime import datetime
import calendar

router = Router()
metrics_service = MetricsService()

def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id == config.ADMIN_USER_ID

def format_month_name(month_key: str) -> str:
    """Convert YYYY-MM to readable format."""
    try:
        year, month = month_key.split('-')
        month_name = calendar.month_name[int(month)]
        return f"{month_name} {year}"
    except:
        return month_key

def create_months_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with available months."""
    all_months = metrics_service.get_all_months()
    buttons = []
    
    # Current month first
    current_month = datetime.now().strftime("%Y-%m")
    if current_month in all_months:
        buttons.append([InlineKeyboardButton(
            text=f"📊 {format_month_name(current_month)} (текущий)",
            callback_data=f"stats_{current_month}"
        )])
    
    # Other months
    for month_key in sorted(all_months.keys(), reverse=True):
        if month_key != current_month:
            buttons.append([InlineKeyboardButton(
                text=f"📊 {format_month_name(month_key)}",
                callback_data=f"stats_{month_key}"
            )])
    
    # All time summary
    buttons.append([InlineKeyboardButton(
        text="📈 Общая статистика",
        callback_data="stats_all"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def format_stats_message(month_key: str, stats) -> str:
    """Format statistics message."""
    if not stats:
        return f"📊 Статистика за {format_month_name(month_key)}\n\n❌ Данных нет"
    
    total_llm = sum(stats.llm_calls.values())
    
    message = f"📊 Статистика за {format_month_name(month_key)}\n\n"
    message += f"👥 Уникальных пользователей: {len(stats.unique_users)}\n"
    message += f"🎙️ Транскрипций: {stats.transcriptions}\n"
    message += f"🤖 LLM обработок: {total_llm}\n\n"
    
    if total_llm > 0:
        message += "📋 По стилям:\n"
        for style, count in stats.llm_calls.items():
            if count > 0:
                style_names = {
                    "proofread": "✍️ Корректура",
                    "my": "⚡ Неформально", 
                    "business": "👔 Деловой",
                    "brief": "📋 Кратко"
                }
                message += f"  {style_names.get(style, style)}: {count}\n"
    
    return message

def format_all_stats_message(all_months) -> str:
    """Format all-time statistics message."""
    if not all_months:
        return "📈 Общая статистика\n\n❌ Данных нет"
    
    total_users = set()
    total_transcriptions = 0
    total_llm = {"proofread": 0, "my": 0, "business": 0, "brief": 0}
    
    for stats in all_months.values():
        total_users.update(stats.unique_users)
        total_transcriptions += stats.transcriptions
        for style, count in stats.llm_calls.items():
            total_llm[style] += count
    
    total_llm_count = sum(total_llm.values())
    
    message = "📈 Общая статистика\n\n"
    message += f"👥 Всего уникальных пользователей: {len(total_users)}\n"
    message += f"🎙️ Всего транскрипций: {total_transcriptions}\n"
    message += f"🤖 Всего LLM обработок: {total_llm_count}\n\n"
    
    if total_llm_count > 0:
        message += "📋 По стилям:\n"
        style_names = {
            "proofread": "✍️ Корректура",
            "my": "⚡ Неформально", 
            "business": "👔 Деловой",
            "brief": "📋 Кратко"
        }
        for style, count in total_llm.items():
            if count > 0:
                message += f"  {style_names.get(style, style)}: {count}\n"
    
    message += f"\n📅 Месяцев с данными: {len(all_months)}"
    
    return message

@router.message(Command("stats"))
async def handle_stats_command(message: Message):
    """Handle /stats command - admin only."""
    if not is_admin(message.from_user.id):
        # Silently ignore for non-admin users
        return
    
    try:
        keyboard = create_months_keyboard()
        await message.answer("📊 Выберите период для просмотра статистики:", reply_markup=keyboard)
        
    except Exception as e:
        logger.error(f"Error in stats command: {str(e)}")
        await message.answer("❌ Ошибка при получении статистики")

@router.callback_query(F.data.startswith("stats_"))
async def process_stats_selection(callback: CallbackQuery):
    """Handle stats period selection."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    
    try:
        await callback.answer()
        
        period = callback.data.replace("stats_", "")
        
        if period == "all":
            all_months = metrics_service.get_all_months()
            message = format_all_stats_message(all_months)
        else:
            stats = metrics_service.get_month_stats(period)
            message = format_stats_message(period, stats)
        
        await callback.message.edit_text(message, reply_markup=create_months_keyboard())
        
    except Exception as e:
        logger.error(f"Error processing stats selection: {str(e)}")
        await callback.message.answer("❌ Ошибка при получении статистики")