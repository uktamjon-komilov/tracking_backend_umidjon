from django.db.models import Q
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from rest_framework.viewsets import GenericViewSet, mixins

from apps.regions.models import District
from apps.users.models import User


class DistrictSerializer(serializers.ModelSerializer):
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = District
        fields = ["id", "name", "employees_count"]

    def get_employees_count(self, obj):
        return User.objects.filter(district=obj).count()


class DistrictsViewSet(GenericViewSet, mixins.ListModelMixin):
    serializer_class = DistrictSerializer

    def get_queryset(self):
        return District.get_districts(request=self.request)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"items": serializer.data})
