from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config.config import config
from services import access_control_service

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_USER_ID


def _extract_target_user(message: Message) -> str | None:
    if message.reply_to_message and message.reply_to_message.from_user:
        return str(message.reply_to_message.from_user.id)

    text = message.text or ""
    parts = text.strip().split(maxsplit=1)
    if len(parts) > 1:
        return parts[1].strip()
    return None


@router.message(Command("vip_add"))
async def handle_vip_add(message: Message):
    if not _is_admin(message.from_user.id):
        return

    target_id = _extract_target_user(message)
    if not target_id:
        await message.answer("❌ Укажите ID пользователя или ответьте на его сообщение.")
        return

    if access_control_service.add_user(target_id):
        await message.answer(f"✅ Пользователь {target_id} теперь в VIP.")
    else:
        await message.answer(f"ℹ️ Пользователь {target_id} уже был в VIP.")


@router.message(Command("vip_remove"))
async def handle_vip_remove(message: Message):
    if not _is_admin(message.from_user.id):
        return

    target_id = _extract_target_user(message)
    if not target_id:
        await message.answer("❌ Укажите ID пользователя или ответьте на его сообщение.")
        return

    if access_control_service.remove_user(target_id):
        await message.answer(f"🗑️ Пользователь {target_id} удалён из VIP.")
    else:
        await message.answer(f"ℹ️ Пользователь {target_id} не найден в VIP.")


@router.message(Command("vip_list"))
async def handle_vip_list(message: Message):
    if not _is_admin(message.from_user.id):
        return

    users = access_control_service.list_users()
    if not users:
        await message.answer("📭 Список VIP пуст.")
        return

    formatted = "\n".join(users)
    await message.answer(f"👑 VIP пользователи ({len(users)}):\n{formatted}")
