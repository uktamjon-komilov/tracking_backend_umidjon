from django.contrib.auth.models import update_last_login
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer  as BaseSerializer
from rest_framework_simplejwt.settings import api_settings


class TokenObtainPairSerializer(BaseSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)
        
        try:
            self.user.app_version = self.initial_data.get("app_version")
            self.user.save()
        except Exception:
            pass

        return data


class TokenObtainPairView(BaseTokenObtainPairView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenRefreshView(BaseTokenRefreshView):
    permission_classes = []
