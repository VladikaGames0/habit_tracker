from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserRegisterView, UserProfileView

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="user-register"),
    path("login/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
]
