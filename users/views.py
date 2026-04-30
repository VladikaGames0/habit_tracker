from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from drf_yasg.utils import swagger_auto_schema

from .serializers import UserRegisterSerializer, UserSerializer

User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(operation_summary="Регистрация пользователя")
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и обновление профиля текущего пользователя."""

    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(operation_summary="Профиль пользователя")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновление профиля (частичное)")
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновление профиля (полное)")
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
