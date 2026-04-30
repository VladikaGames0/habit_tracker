"""
Telegram-бот для трекера привычек.

Команды:
    /start  — привязать Telegram к аккаунту
    /habits — список своих привычек
    /help   — справка
"""
import logging
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Привязать Telegram chat_id к аккаунту пользователя."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    chat_id = str(update.effective_chat.id)
    username = update.effective_user.username or ""

    user = await sync_to_async(User.objects.filter(username=username).first)()
    if user:
        user.telegram_chat_id = chat_id
        await sync_to_async(user.save)(update_fields=["telegram_chat_id"])
        await update.message.reply_text(
            f"✅ Привет, {user.username}!\n"
            "Telegram успешно привязан. Теперь вы будете получать напоминания о привычках!"
        )
    else:
        await update.message.reply_text(
            f"👋 Привет!\n"
            f"Ваш Chat ID: <code>{chat_id}</code>\n\n"
            "Укажите этот ID в профиле на сайте в поле <b>telegram_chat_id</b>.\n"
            "Или зарегистрируйтесь с username, совпадающим с вашим Telegram username.",
            parse_mode="HTML",
        )


async def habits_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показать список привычек пользователя."""
    from habits.models import Habit
    from django.contrib.auth import get_user_model
    User = get_user_model()

    chat_id = str(update.effective_chat.id)
    user = await sync_to_async(User.objects.filter(telegram_chat_id=chat_id).first)()

    if not user:
        await update.message.reply_text(
            "❌ Аккаунт не найден. Используйте /start для привязки."
        )
        return

    habits = await sync_to_async(
        lambda: list(Habit.objects.filter(user=user).order_by("time")[:10])
    )()

    if not habits:
        await update.message.reply_text("У вас пока нет привычек.")
        return

    text = "📋 <b>Ваши привычки:</b>\n\n"
    for h in habits:
        emoji = "😊" if h.is_pleasant else "💪"
        text += f"{emoji} {h.action} — {h.time.strftime('%H:%M')} ({h.place})\n"

    await update.message.reply_text(text, parse_mode="HTML")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "🤖 <b>Трекер привычек</b>\n\n"
        "/start  — привязать Telegram к аккаунту\n"
        "/habits — список ваших привычек\n"
        "/help   — эта справка\n\n"
        "Бот автоматически пришлёт напоминание в нужное время."
    )
    await update.message.reply_text(text, parse_mode="HTML")


def main() -> None:
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не задан в .env")
        return

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("habits", habits_list))
    app.add_handler(CommandHandler("help", help_command))

    logger.info("Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    main()