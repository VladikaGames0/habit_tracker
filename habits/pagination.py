from rest_framework.pagination import LimitOffsetPagination


class HabitPagination(LimitOffsetPagination):
    """
    Пагинация привычек: 5 на страницу.
    Поля ответа: count, next, previous, results.
    Параметры запроса: ?limit=5&offset=0
    """
    default_limit = 5
    max_limit = 50
