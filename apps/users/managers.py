from django.contrib.auth.models import UserManager as BaseManager
from django.core.exceptions import ValidationError


class UserManager(BaseManager):
    def create_user(self, username, password=None):
        if not password:
            raise ValidationError("Password must be set")

        user = self.model(username=username)
        user.set_password(password)
        user.is_active = True
        user.save()

        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user
