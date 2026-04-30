from rest_framework import serializers

from .models import Habit
from .validators import (
    validate_reward_or_related_habit,
    validate_duration,
    validate_related_habit_is_pleasant,
    validate_pleasant_habit_has_no_reward_or_related,
    validate_periodicity,
)


class HabitSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Habit
        fields = (
            "id", "user", "place", "time", "action", "is_pleasant",
            "related_habit", "periodicity", "reward", "duration",
            "is_public", "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        instance = self.instance

        reward = attrs.get("reward", instance.reward if instance else None)
        related_habit = attrs.get("related_habit", instance.related_habit if instance else None)
        is_pleasant = attrs.get("is_pleasant", instance.is_pleasant if instance else False)
        duration = attrs.get("duration", instance.duration if instance else None)
        periodicity = attrs.get("periodicity", instance.periodicity if instance else 1)

        validate_reward_or_related_habit(reward, related_habit)
        validate_related_habit_is_pleasant(related_habit)
        validate_pleasant_habit_has_no_reward_or_related(is_pleasant, reward, related_habit)
        validate_periodicity(periodicity)
        if duration is not None:
            validate_duration(duration)

        return attrs


class PublicHabitSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Habit
        fields = (
            "id", "user", "place", "time", "action", "is_pleasant",
            "related_habit", "periodicity", "reward", "duration", "is_public",
        )
