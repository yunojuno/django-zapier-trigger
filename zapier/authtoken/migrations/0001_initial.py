# Generated by Django 4.1 on 2022-09-04 10:14

import uuid

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuthToken",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "api_token",
                    models.UUIDField(
                        default=uuid.uuid4,
                        help_text="API token for use in Zapier integration",
                    ),
                ),
                (
                    "api_scopes",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="List of strings used to define access permissions.",
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("last_updated_at", models.DateTimeField()),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="zapier_token",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TokenAuthRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "token",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="auth_requests",
                        to="authtoken.authtoken",
                    ),
                ),
            ],
            options={
                "get_latest_by": "timestamp",
            },
        ),
    ]
