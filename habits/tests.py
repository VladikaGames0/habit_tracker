import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError

from habits.models import Habit
from habits.validators import (
    validate_duration,
    validate_periodicity,
    validate_pleasant_habit_has_no_reward_or_related,
    validate_related_habit_is_pleasant,
    validate_reward_or_related_habit,
)

User = get_user_model()


# ── Фикстуры ─────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="other", email="other@example.com", password="otherpass123"
    )


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def pleasant_habit(db, user):
    return Habit.objects.create(
        user=user, place="Дом", time="08:00",
        action="Выпить кофе", is_pleasant=True, duration=60, periodicity=1,
    )


@pytest.fixture
def useful_habit(db, user, pleasant_habit):
    return Habit.objects.create(
        user=user, place="Парк", time="07:00",
        action="Пробежка", is_pleasant=False, duration=90,
        periodicity=1, related_habit=pleasant_habit,
    )


# ── Тесты валидаторов ─────────────────────────────────────

class TestValidators:
    def test_reward_and_related_together_raises(self, pleasant_habit):
        with pytest.raises(ValidationError):
            validate_reward_or_related_habit("Шоколадка", pleasant_habit)

    def test_reward_only_ok(self):
        validate_reward_or_related_habit("Шоколадка", None)

    def test_related_only_ok(self, pleasant_habit):
        validate_reward_or_related_habit(None, pleasant_habit)

    def test_duration_over_120_raises(self):
        with pytest.raises(ValidationError):
            validate_duration(121)

    def test_duration_120_ok(self):
        validate_duration(120)

    def test_related_not_pleasant_raises(self, useful_habit):
        with pytest.raises(ValidationError):
            validate_related_habit_is_pleasant(useful_habit)

    def test_related_pleasant_ok(self, pleasant_habit):
        validate_related_habit_is_pleasant(pleasant_habit)

    def test_pleasant_with_reward_raises(self):
        with pytest.raises(ValidationError):
            validate_pleasant_habit_has_no_reward_or_related(True, "Шоколадка", None)

    def test_pleasant_with_related_raises(self, pleasant_habit):
        with pytest.raises(ValidationError):
            validate_pleasant_habit_has_no_reward_or_related(True, None, pleasant_habit)

    def test_periodicity_zero_raises(self):
        with pytest.raises(ValidationError):
            validate_periodicity(0)

    def test_periodicity_eight_raises(self):
        with pytest.raises(ValidationError):
            validate_periodicity(8)

    def test_periodicity_valid_range(self):
        for p in range(1, 8):
            validate_periodicity(p)


# ── Тесты модели ─────────────────────────────────────────

class TestHabitModel:
    def test_str_representation(self, useful_habit):
        assert "Пробежка" in str(useful_habit)
        assert "Парк" in str(useful_habit)

    def test_default_periodicity(self, db, user):
        h = Habit.objects.create(user=user, place="Дом", time="10:00", action="Зарядка", duration=60)
        assert h.periodicity == 1

    def test_is_public_default_false(self, db, user):
        h = Habit.objects.create(user=user, place="Дом", time="10:00", action="Медитация", duration=60)
        assert h.is_public is False


# ── Тесты эндпоинтов ──────────────────────────────────────

class TestHabitEndpoints:
    def test_list_requires_auth(self, api_client):
        url = reverse("habit-list-create")
        assert api_client.get(url).status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_returns_only_own_habits(self, auth_client, useful_habit, other_user, db):
        Habit.objects.create(user=other_user, place="Офис", time="09:00", action="Читать", duration=60)
        url = reverse("habit-list-create")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for result in response.data["results"]:
            assert result["action"] != "Читать"

    def test_create_habit_success(self, auth_client, pleasant_habit):
        url = reverse("habit-list-create")
        data = {
            "place": "Спортзал", "time": "18:00", "action": "Жим лёжа",
            "is_pleasant": False, "duration": 90, "periodicity": 2,
            "related_habit": pleasant_habit.pk,
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["action"] == "Жим лёжа"

    def test_create_reward_and_related_fails(self, auth_client, pleasant_habit):
        url = reverse("habit-list-create")
        data = {
            "place": "Парк", "time": "07:00", "action": "Бег",
            "duration": 90, "reward": "Мороженое", "related_habit": pleasant_habit.pk,
        }
        assert auth_client.post(url, data).status_code == status.HTTP_400_BAD_REQUEST

    def test_create_duration_over_120_fails(self, auth_client):
        url = reverse("habit-list-create")
        data = {"place": "Дом", "time": "08:00", "action": "Растяжка", "duration": 200}
        assert auth_client.post(url, data).status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_own_habit(self, auth_client, useful_habit):
        url = reverse("habit-detail", kwargs={"pk": useful_habit.pk})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["action"] == useful_habit.action

    def test_retrieve_other_user_habit_forbidden(self, auth_client, other_user, db):
        other = Habit.objects.create(
            user=other_user, place="Кафе", time="11:00", action="Газета", duration=60
        )
        url = reverse("habit-detail", kwargs={"pk": other.pk})
        assert auth_client.get(url).status_code == status.HTTP_404_NOT_FOUND

    def test_update_habit(self, auth_client, useful_habit):
        url = reverse("habit-detail", kwargs={"pk": useful_habit.pk})
        response = auth_client.patch(url, {"place": "Набережная"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["place"] == "Набережная"

    def test_delete_habit(self, auth_client, useful_habit):
        url = reverse("habit-detail", kwargs={"pk": useful_habit.pk})
        assert auth_client.delete(url).status_code == status.HTTP_204_NO_CONTENT
        assert not Habit.objects.filter(pk=useful_habit.pk).exists()

    def test_public_habits_list(self, auth_client, other_user, db):
        Habit.objects.create(
            user=other_user, place="Стадион", time="06:00",
            action="Пробежка", duration=90, is_public=True,
        )
        url = reverse("habit-public-list")
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_public_habits_no_post(self, auth_client):
        assert (
            auth_client.post(reverse("habit-public-list"), {}).status_code
            == status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_pleasant_habit_no_reward_fails(self, auth_client):
        url = reverse("habit-list-create")
        data = {
            "place": "Дом", "time": "09:00", "action": "Кофе",
            "is_pleasant": True, "duration": 60, "reward": "Шоколад",
        }
        assert auth_client.post(url, data).status_code == status.HTTP_400_BAD_REQUEST

    def test_periodicity_over_7_fails(self, auth_client):
        url = reverse("habit-list-create")
        data = {
            "place": "Дом", "time": "09:00", "action": "Книга",
            "duration": 60, "periodicity": 8,
        }
        assert auth_client.post(url, data).status_code == status.HTTP_400_BAD_REQUEST


# ── Тесты пагинации (LimitOffsetPagination) ───────────────

class TestPagination:
    def test_default_page_size_is_5(self, auth_client, user, db):
        for i in range(7):
            Habit.objects.create(
                user=user, place=f"Место {i}", time="10:00",
                action=f"Действие {i}", duration=60,
            )
        response = auth_client.get(reverse("habit-list-create"))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5
        assert response.data["count"] == 7
        assert response.data["next"] is not None

    def test_offset_pagination(self, auth_client, user, db):
        for i in range(7):
            Habit.objects.create(
                user=user, place=f"Место {i}", time="10:00",
                action=f"Действие {i}", duration=60,
            )
        response = auth_client.get(reverse("habit-list-create") + "?limit=5&offset=5")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_response_structure(self, auth_client, useful_habit):
        response = auth_client.get(reverse("habit-list-create"))
        assert "count" in response.data
        assert "results" in response.data
        assert "next" in response.data
        assert "previous" in response.data


# ── Тесты авторизации ─────────────────────────────────────

class TestUserAuth:
    def test_register(self, api_client, db):
        response = api_client.post(reverse("user-register"), {
            "email": "new@example.com", "username": "newuser", "password": "securepass123",
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert "password" not in response.data

    def test_login_success(self, api_client, user):
        response = api_client.post(reverse("token-obtain-pair"), {
            "email": "test@example.com", "password": "testpass123",
        })
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_login_wrong_password(self, api_client, user):
        response = api_client.post(reverse("token-obtain-pair"), {
            "email": "test@example.com", "password": "wrong",
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
