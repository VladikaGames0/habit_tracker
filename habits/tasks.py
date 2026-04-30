import logging

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def _send_telegram(chat_id: str, message: str) -> bool:
    """
    Отправка сообщения через Telegram Bot API (синхронный HTTP-запрос).
    Не используем asyncio внутри Celery — это вызывает конфликты event loop.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN не задан — сообщение не отправлено")
        return False

    url = TELEGRAM_API_URL.format(token=token)
    try:
        response = requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=10,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.error("Ошибка Telegram для chat_id=%s: %s", chat_id, exc)
        return False


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_habit_reminder(self, habit_id: int) -> str:
    """Отправить напоминание о конкретной привычке пользователю в Telegram."""
    from habits.models import Habit

    try:
        habit = Habit.objects.select_related("user", "related_habit").get(pk=habit_id)
    except Habit.DoesNotExist:
        return f"Привычка {habit_id} не найдена"

    user = habit.user
    if not user.telegram_chat_id:
        return f"У пользователя {user.email} нет Telegram chat_id"

    message = (
        f"⏰ <b>Напоминание о привычке</b>\n\n"
        f"🎯 <b>Действие:</b> {habit.action}\n"
        f"📍 <b>Место:</b> {habit.place}\n"
        f"🕐 <b>Время:</b> {habit.time.strftime('%H:%M')}\n"
        f"⏱ <b>Длительность:</b> {habit.duration} сек.\n"
    )
    if habit.reward:
        message += f"🎁 <b>Награда:</b> {habit.reward}\n"
    if habit.related_habit:
        message += f"😊 <b>Приятная привычка:</b> {habit.related_habit.action}\n"

    success = _send_telegram(user.telegram_chat_id, message)
    if not success:
        raise self.retry(exc=Exception("Ошибка отправки Telegram"))
    return f"Отправлено: привычка {habit_id}"


@shared_task
def check_and_send_reminders() -> str:
    """
    Периодическая задача — каждую минуту проверяет привычки,
    у которых время совпадает с текущим, и рассылает напоминания.

    Настроить в Django Admin → Periodic Tasks:
      - Task: habits.tasks.check_and_send_reminders
      - Crontab: * * * * * (каждую минуту)
    """
    from habits.models import Habit

    now = timezone.localtime(timezone.now())
    current_hour = now.hour
    current_minute = now.minute

    habits = Habit.objects.filter(
        user__telegram_chat_id__isnull=False,
        time__hour=current_hour,
        time__minute=current_minute,
    ).select_related("user")

    count = 0
    for habit in habits:
        send_habit_reminder.delay(habit.pk)
        count += 1

    logger.info("Запущено %d напоминаний в %02d:%02d", count, current_hour, current_minute)
    return f"Запущено {count} напоминаний"
