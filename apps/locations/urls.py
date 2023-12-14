from rest_framework.routers import DefaultRouter

from django.urls import include, path

from apps.locations.views import GeolocationViewSet, ObserveViewSet


router = DefaultRouter()
router.register("", GeolocationViewSet, "geolocation")
router.register("observe", ObserveViewSet, "observe")


urlpatterns = [
    path("", include(router.urls)),
]
