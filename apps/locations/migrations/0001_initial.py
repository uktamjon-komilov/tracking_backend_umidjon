# Generated by Django 4.2 on 2023-12-14 13:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Geolocation',
            fields=[
                ('id', models.CharField(default=uuid.uuid4, editable=False, max_length=36, primary_key=True, serialize=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('longitude', models.DecimalField(decimal_places=10, max_digits=14)),
                ('latitude', models.DecimalField(decimal_places=10, max_digits=14)),
                ('timestamp', models.DateTimeField()),
                ('received_from', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='geolocations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]