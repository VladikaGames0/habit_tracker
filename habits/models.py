from django.db import models
from django.conf import settings


class Habit(models.Model):
    """Модель привычки."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время выполнения")
    action = models.CharField(max_length=500, verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_habits",
        verbose_name="Связанная привычка",
    )
    periodicity = models.PositiveIntegerField(
        default=1,
        verbose_name="Периодичность (дней)",
    )
    reward = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
    )
    duration = models.PositiveIntegerField(
        verbose_name="Время на выполнение (сек)",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Публичная привычка",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} — {self.action} в {self.time} ({self.place})"
