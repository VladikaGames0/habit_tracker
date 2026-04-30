from rest_framework import generics, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Habit
from .serializers import HabitSerializer, PublicHabitSerializer
from .permissions import IsOwner
from .pagination import HabitPagination


class HabitListCreateView(generics.ListCreateAPIView):
    """Список и создание привычек текущего пользователя."""

    serializer_class = HabitSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).select_related("related_habit")

    @swagger_auto_schema(
        operation_summary="Список привычек пользователя",
        operation_description="Возвращает привычки текущего пользователя (5 на страницу). "
                              "Параметры: limit, offset.",
        manual_parameters=[
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Количество записей"),
            openapi.Parameter("offset", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description="Смещение"),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создание привычки",
        responses={201: HabitSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class HabitRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление привычки (только владелец)."""

    serializer_class = HabitSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner)

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).select_related("related_habit")

    @swagger_auto_schema(operation_summary="Получение привычки")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Полное обновление привычки")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление привычки")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Удаление привычки", responses={204: "No Content"})
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class PublicHabitListView(generics.ListAPIView):
    """Список публичных привычек (только чтение, без редактирования)."""

    serializer_class = PublicHabitSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = HabitPagination

    def get_queryset(self):
        return Habit.objects.filter(is_public=True).select_related("user", "related_habit")

    @swagger_auto_schema(
        operation_summary="Публичные привычки",
        operation_description="Список публичных привычек всех пользователей. Только чтение.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
