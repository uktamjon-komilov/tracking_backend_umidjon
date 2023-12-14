import uuid
from django.db import models


class Model(models.Model):
    id = models.CharField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        max_length=36,
    )

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
