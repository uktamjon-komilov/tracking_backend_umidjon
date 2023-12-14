from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.regions.views import DistrictsViewSet


router = DefaultRouter()
router.register("districts", DistrictsViewSet, basename="districts")


urlpatterns = [
    path("", include(router.urls)),
]
