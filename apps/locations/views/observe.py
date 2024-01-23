import random
import contextlib
import numpy as np

from django.utils.timezone import datetime, timedelta, make_aware, get_current_timezone
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import mixins, GenericViewSet

from apps.regions.models import District
from apps.locations.models import Geolocation
from apps.users.models import User


background_colors = [
    "#3498db",  # Dodger Blue
    "#2ecc71",  # Emerald Green
    "#e74c3c",  # Alizarin Crimson
    "#f39c12",  # Orange
    "#1abc9c",  # Turquoise
    "#9b59b6",  # Amethyst
    "#34495e",  # Wet Asphalt
    "#2c3e50",  # Midnight Blue
    "#27ae60",  # Nephritis
    "#d35400",  # Pumpkin
    "#16a085",  # Green Sea
    "#c0392b",  # Pomegranate
    "#f1c40f",  # Sunflower Yellow
    "#8e44ad",  # Wisteria
    "#95a5a6",  # Concrete
    "#d35400",  # Pumpkin
    "#3498db",  # Dodger Blue
    "#2ecc71",  # Emerald Green
    "#e74c3c",  # Alizarin Crimson
    "#f39c12",  # Orange
]


def calculate_centroid(locations):
    if not locations:
        return None

    total_longitude = 0
    total_latitude = 0
    count = 0

    for location in locations:
        total_longitude += location["longitude"]
        total_latitude += location["latitude"]
        count += 1

    return {
        "longitude": total_longitude / count,
        "latitude": total_latitude / count,
    }


def calculate_bounds(locations):
    if not locations:
        return None

    min_lat = min(float(location["latitude"]) for location in locations)
    max_lat = max(float(location["latitude"]) for location in locations)
    min_lon = min(float(location["longitude"]) for location in locations)
    max_lon = max(float(location["longitude"]) for location in locations)

    return (min_lat, max_lat, min_lon, max_lon)


def calculate_zoom_level(locations, map_width, map_height):
    bounds = calculate_bounds(locations)
    if not bounds:
        return None

    WORLD_WIDTH = 256
    ZOOM_MAX = 21

    lat_ratio = (bounds[1] - bounds[0]) / 180
    lon_ratio = (bounds[3] - bounds[2]) / 360

    zoom_lat = -1 * np.log2(lat_ratio) + np.log2(map_height / WORLD_WIDTH)
    zoom_lon = -1 * np.log2(lon_ratio) + np.log2(map_width / WORLD_WIDTH)

    zoom = min(zoom_lat, zoom_lon, ZOOM_MAX)
    return max(0, min(zoom, ZOOM_MAX))


class ObserveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = District.get_districts()

    def list(self, request, *args, **kwargs):
        districts = self.get_queryset()

        if request.user.district:
            districts = districts.filter(district=request.user.district)

        result = {"districts": []}

        for district in districts:
            employee_count = User.objects.filter(district=district).count()
            data = {
                "id": district.id,
                "name": district.name,
                "centroid_longitude": district.centroid_longitude,
                "centroid_latitude": district.centroid_latitude,
                "employee_count": employee_count,
                "background_color": random.choice(background_colors),
            }
            result["districts"].append(data)

        return Response(result)

    def retrieve(self, request, *args, **kwargs):
        district = self.get_object()

        users = User.objects.filter(district=district)

        officers = []
        for user in users:
            location = (
                Geolocation.objects.filter(received_from=user)
                .order_by("-timestamp")
                .first()
            )

            officers.append(
                {
                    **self.get_location_dict(location=location),
                    "received_from": str(user),
                    "short_name": user.short_name,
                    "user_id": user.id,
                    "has_not_updated_recently": not self.check_if_recently_updated(
                        location
                    ),
                }
            )

        officers.sort(key=lambda officer: officer["has_not_updated_recently"] is False)

        result = {
            "officers": officers,
            "district": {
                "id": district.id,
                "name": district.name,
                "centroid_longitude": district.centroid_longitude,
                "centroid_latitude": district.centroid_latitude,
            },
        }
        return Response(result)

    @action(detail=True, methods=["get"], url_path="user_history")
    def user_location_history(self, request, *args, **kwargs):
        user_id = request.query_params.get("user_id")
        if not user_id:
            raise ValidationError({"user_id": "query param is required"})

        user = User.objects.filter(id=user_id).first()

        if not user:
            raise ValidationError({"user_id": "User doesn't exist"})

        locations = Geolocation.objects.filter(received_from=user).order_by(
            "-timestamp"
        )

        last_location = locations.first()
        locations = self.filter_by_datetime_range(locations, request)

        locations_data = [
            {
                "id": location.id,
                "longitude": location.longitude,
                "latitude": location.latitude,
            }
            for location in locations
        ]

        result = {
            "officer": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": user.middle_name,
                "phone": user.phone,
                "duty_areas": str(user.district),
                "photo": self.get_photo_url(request, user),
                "has_not_updated_recently": not self.check_if_recently_updated(
                    last_location
                ),
            },
            "metadata": {
                "centroid": calculate_centroid(locations=locations_data),
                "zoom_level": calculate_zoom_level(
                    locations=locations_data,
                    map_width=1500,
                    map_height=1000,
                ),
            },
            "locations": locations_data if locations_data else None,
        }
        return Response(result)

    def check_if_recently_updated(self, location):
        if location is None:
            return False

        now_timezone_aware = make_aware(datetime.now(), get_current_timezone())

        return (now_timezone_aware - location.timestamp).seconds < 600

    def get_photo_url(self, request, user: User):
        try:
            return (
                None
                if user.photo is None
                else request.build_absolute_uri(user.photo.url)
            )
        except:
            return None

    def filter_by_datetime_range(self, locations, request):
        now_timezone_aware = make_aware(datetime.now(), get_current_timezone())

        with contextlib.suppress(Exception):
            start_datetime = datetime.strptime(
                request.query_params.get(
                    "start_datetime",
                    (now_timezone_aware - timedelta(hours=3)).strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    ),
                ),
                "%Y-%m-%dT%H:%M:%S",
            )
            locations = locations.filter(timestamp__gte=start_datetime)

        with contextlib.suppress(Exception):
            end_datetime = datetime.strptime(
                request.query_params.get(
                    "end_datetime",
                    now_timezone_aware.strftime("%Y-%m-%dT%H:%M:%S"),
                ),
                "%Y-%m-%dT%H:%M:%S",
            )
            locations = locations.filter(timestamp__lte=end_datetime)

        return locations

    def get_location_dict(self, location: Geolocation | None) -> dict:
        if location is None:
            return {
                "id": None,
                "longitude": None,
                "latitude": None,
            }

        return {
            "id": location.id,
            "longitude": location.longitude,
            "latitude": location.latitude,
        }
