from django.db.models import (
    CharField,
    IntegerField,
    ForeignKey,
    DecimalField,
    SET_NULL,
)

from apps.shared.models import Model


COUNTRY = "O'zbekiston"


class Region(Model):
    name = CharField(max_length=50)

    def __str__(self):
        return self.name


class District(Model):
    region = ForeignKey(Region, on_delete=SET_NULL, null=True, related_name="districts")
    name = CharField(max_length=50)
    centroid_longitude = DecimalField(max_digits=14, decimal_places=10)
    centroid_latitude = DecimalField(max_digits=14, decimal_places=10)
    radius_in_km = IntegerField(default=70)
    user_color = CharField(max_length=10, default="#0000ff")

    def __str__(self):
        return self.name

    @staticmethod
    def get_districts(request=None, **kwargs):
        qs = District.objects.filter(region__name=COUNTRY, **kwargs)

        if request:
            user = request.user
            if not user.is_superuser and user.district:
                qs = qs.filter(id=user.district.id)

        return qs
