from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views.auth import TokenObtainPairView, TokenRefreshView
from apps.users.views.users import UsersViewSet


router = DefaultRouter()
router.register("", UsersViewSet, basename="users")


urlpatterns = [
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
