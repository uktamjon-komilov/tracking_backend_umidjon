from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/locations/", include("apps.locations.urls")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/regions/", include("apps.regions.urls")),
    path("/", include("apps.website.urls")),
]
