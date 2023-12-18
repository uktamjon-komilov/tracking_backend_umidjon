import traceback

from django.db import transaction
from django.contrib.gis.geos import Point
from rest_framework.decorators import action
from rest_framework.viewsets import mixins, GenericViewSet
from rest_framework import serializers
from rest_framework.response import Response

from apps.locations.models import Geolocation

from .observe import ObserveViewSet


class GeolocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geolocation
        fields = ["longitude", "latitude", "timestamp"]


class GeolocationBatchItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geolocation
        fields = ["longitude", "latitude", "timestamp"]


class GeolocationBatchSaveSerializer(serializers.Serializer):
    locations = serializers.ListField(child=GeolocationBatchItemSerializer())


class GeolocationViewSet(GenericViewSet, mixins.CreateModelMixin):
    queryset = Geolocation.objects.all()
    serializer_class = GeolocationSerializer

    def get_serializer_class(self):
        if self.action in ["save_batch_locations"]:
            return GeolocationBatchSaveSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            raise e

        point = Point(
            x=serializer.validated_data["longitude"],
            y=serializer.validated_data["latitude"],
        )
        try:
            serializer.save(
                location=point,
                received_from=request.user,
            )
        except Exception as e:
            return Response(
                {
                    "ok": False,
                    "traceback": str(traceback.format_exc()),
                    "error": str(e),
                }
            )

        return Response({"ok": True})

    @action(detail=False, methods=["post"], url_path="save_batch")
    @transaction.atomic()
    def save_batch_locations(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            raise e

        try:
            for item in serializer.validated_data["locations"]:
                point = Point(
                    x=serializer.validated_data["longitude"],
                    y=serializer.validated_data["latitude"],
                )
                location = Geolocation(
                    location=point,
                    longitude=item["longitude"],
                    latitude=item["latitude"],
                    timestamp=item["timestamp"],
                    received_from=request.user,
                )
                location.save()
        except Exception as e:
            transaction.set_rollback(rollback=True)
            return Response(
                {
                    "ok": False,
                    "traceback": str(traceback.format_exc()),
                    "error": str(e),
                }
            )

        return Response({"ok": True})
