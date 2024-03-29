from django.db import models

from apps.shared.models import Model


class Geolocation(Model):
    longitude = models.DecimalField(max_digits=14, decimal_places=10)
    latitude = models.DecimalField(max_digits=14, decimal_places=10)
    received_from = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        null=True,
        related_name="geolocations",
    )
    timestamp = models.DateTimeField()

    def __str__(self) -> str:
        return "Location({}, {})".format(self.longitude, self.latitude)
