from django.db.models import Q
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.pagination import PageNumberPagination

from apps.users.models import User
from apps.regions.models import District


class UserFilters(filters.FilterSet):
    search_query = filters.CharFilter(method="filter_by_search_query")

    class Meta:
        model = User
        fields = ["district", "search_query"]

    def filter_by_search_query(self, queryset, name, value):
        parts = set(filter(lambda x: bool(str(x).strip()), value.split()))

        query = Q()
        for term in parts:
            query |= Q(
                Q(first_name__icontains=term)
                | Q(last_name__icontains=term)
                | Q(middle_name__icontains=term)
                | Q(username__icontains=term)
                | Q(phone__icontains=term)
            )

        return queryset.filter(query)


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(many=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "photo",
            "district",
            "is_active",
            "has_observation_access",
            "has_management_access",
            "has_editing_staff_access",
        ]


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "photo",
            "district",
        ]


class UserSaveSerializer(serializers.ModelSerializer):
    password = serializers.CharField(allow_null=True, allow_blank=True)
    photo = serializers.ImageField(allow_null=True)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "photo",
            "district",
            "is_active",
        ]

    def validate_photo(self, value):
        if not value or isinstance(value, str):
            return None
        return value

    def save(self, **kwargs):
        password = self.validated_data.pop("password", None)
        photo = self.validated_data.pop("photo", None)

        if not self.partial or photo:
            instance = super().save(**kwargs, photo=photo)
        else:
            instance = super().save(**kwargs)

        if password:
            instance.set_password(password)
            instance.save()

        return instance


class UpdateCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]

    def save(self, **kwargs):
        password = self.validated_data.pop("password", None)
        instance = super().save(**kwargs)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class UsersViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UserFilters
    ordering = ("-created_at",)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return UserSaveSerializer
        elif self.action == "update_credentials":
            return UpdateCredentialsSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_superuser and user.district:
            qs = qs.filter(district=user.district)

        return qs
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        instance.is_active = True
        instance.save()
        return Response({})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        super().update(request, *args, **kwargs)
        User.refresh_from_db(instance)
        return Response(UserSerializer(instance).data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        super().partial_update(request, *args, **kwargs)
        User.refresh_from_db(instance)
        return Response(UserSerializer(instance).data)

    @action(detail=False, methods=["get"], url_path="me")
    def get_my_details(self, request, *args, **kwargs):
        return Response(
            {
                "user_details": UserDetailsSerializer(
                    request.user,
                    context=self.get_serializer_context(),
                ).data,
                "permissions": {
                    "has_observation_access": request.user.has_observation_access,
                    "has_management_access": request.user.has_management_access,
                    "has_editing_staff_access": request.user.has_editing_staff_access,
                }
            }
        )

    @action(detail=True, methods=["patch"], url_path="update_credentials")
    def update_credentials(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UpdateCredentialsSerializer(
            instance=instance,
            data=request.data,
            partial=True,
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(UserSerializer(instance).data)
