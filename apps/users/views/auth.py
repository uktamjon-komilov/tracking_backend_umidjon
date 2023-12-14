from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)


class TokenObtainPairView(BaseTokenObtainPairView):
    permission_classes = []


class TokenRefreshView(BaseTokenRefreshView):
    permission_classes = []
