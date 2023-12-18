import random
import contextlib

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


class ObserveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    queryset = District.get_districts()

    def list(self, request, *args, **kwargs):
        districts = self.get_queryset()

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

        result = {"officers": officers}
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
                "photo": None
                if user.photo is None
                else request.build_absolute_uri(user.photo.url),
                "has_not_updated_recently": not self.check_if_recently_updated(
                    last_location
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
