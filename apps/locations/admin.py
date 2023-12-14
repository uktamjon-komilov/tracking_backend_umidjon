from django.contrib import admin

from apps.locations.models import Geolocation


class GeolocationAdmin(admin.ModelAdmin):
    list_display = ["longitude", "latitude", "timestamp", "created_at"]
    list_filter = ["received_from"]


admin.site.register(Geolocation, GeolocationAdmin)
