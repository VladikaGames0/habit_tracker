from rest_framework.exceptions import ValidationError


def validate_reward_or_related_habit(reward, related_habit):
    """Нельзя указывать одновременно вознаграждение и связанную привычку."""
    if reward and related_habit:
        raise ValidationError(
            "Нельзя одновременно указывать вознаграждение и связанную привычку."
        )


def validate_duration(duration):
    """Время выполнения не более 120 секунд."""
    if duration > 120:
        raise ValidationError(
            "Время выполнения не должно превышать 120 секунд."
        )


def validate_related_habit_is_pleasant(related_habit):
    """Связанная привычка должна быть приятной."""
    if related_habit and not related_habit.is_pleasant:
        raise ValidationError(
            "Связанной может быть только приятная привычка."
        )


def validate_pleasant_habit_has_no_reward_or_related(is_pleasant, reward, related_habit):
    """У приятной привычки не может быть вознаграждения или связанной привычки."""
    if is_pleasant:
        if reward:
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения."
            )
        if related_habit:
            raise ValidationError(
                "У приятной привычки не может быть связанной привычки."
            )


def validate_periodicity(periodicity):
    """Периодичность от 1 до 7 дней."""
    if periodicity < 1 or periodicity > 7:
        raise ValidationError(
            "Периодичность должна быть от 1 до 7 дней."
        )
