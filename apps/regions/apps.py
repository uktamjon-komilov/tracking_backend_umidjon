from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError


class RegionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.regions"

    def ready(self) -> None:
        from apps.regions.utils import get_or_create_districts

        try:
            get_or_create_districts()
        except (OperationalError, ProgrammingError):
            pass
