# Generated by Django 4.1 on 2022-08-16 15:24

import django.core.serializers.json
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zapier", "0006_alter_resthooksubscription_scope_and_more"),
    ]

    operations = [
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
                        to="zapier.resthooksubscription",
                    ),
                ),
            ],
        ),
    ]
