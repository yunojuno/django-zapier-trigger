# Generated by Django 4.1.1 on 2022-09-09 08:29

import uuid

import django.core.serializers.json
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
            name="RestHookSubscription",
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
                ("uuid", models.UUIDField(default=uuid.uuid4, help_text="Public ID")),
                (
                    "trigger",
                    models.CharField(
                        db_index=True,
                        help_text="The name of the trigger event to subscribe to.",
                        max_length=50,
                    ),
                ),
                (
                    "target_url",
                    models.URLField(
                        help_text="The webhook URL to which any payload will be POSTed."
                    ),
                ),
                (
                    "subscribed_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Timestamp marking when the initial subscribe event occurred.",
                    ),
                ),
                (
                    "unsubscribed_at",
                    models.DateTimeField(
                        blank=True,
                        default=None,
                        help_text="Timestamp marking when the unsubscribe event occurred.",
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rest_hooks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RestHookEvent",
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
                    "started_at",
                    models.DateTimeField(
                        blank=True, default=django.utils.timezone.now, null=True
                    ),
                ),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                (
                    "request_payload",
                    models.JSONField(
                        blank=True,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                        null=True,
                    ),
                ),
                (
                    "response_payload",
                    models.JSONField(
                        blank=True,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                        null=True,
                    ),
                ),
                ("status_code", models.IntegerField()),
                (
                    "subscription",
                    models.ForeignKey(
                        help_text="The subscription to which the event was posted.",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="hooks.resthooksubscription",
                    ),
                ),
            ],
        ),
    ]
