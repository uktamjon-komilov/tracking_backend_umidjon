from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)
from django.db.models import (
    CharField,
    BooleanField,
    ImageField,
    ForeignKey,
    SET_NULL,
)

from apps.shared.models import Model
from apps.users.managers import UserManager


class User(Model, AbstractBaseUser, PermissionsMixin):
    username = CharField(max_length=60, unique=True)
    first_name = CharField(max_length=50, null=True)
    last_name = CharField(max_length=50, null=True)
    middle_name = CharField(max_length=50, null=True)
    phone = CharField(max_length=50, null=True)
    photo = ImageField(upload_to="profile/", null=True)
    district = ForeignKey(
        "regions.District",
        on_delete=SET_NULL,
        null=True,
        related_name="users",
    )

    is_staff = BooleanField(default=False)
    is_active = BooleanField(default=True)

    has_observation_access = BooleanField(default=False)
    has_management_access = BooleanField(default=False)
    has_editing_staff_access = BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return "{} {} {}".format(
            self.first_name or "",
            self.last_name or "",
            self.middle_name or "",
        )

    @property
    def short_name(self):
        return "{} {}. {}.".format(
            self.first_name or "",
            (self.last_name or "-")[0],
            (self.middle_name or "-")[0],
        )
