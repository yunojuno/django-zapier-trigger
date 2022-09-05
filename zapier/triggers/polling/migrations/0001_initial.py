# Generated by Django 4.1.1 on 2022-09-05 16:17

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
            name="PollingTriggerRequest",
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
                ("scope", models.CharField(max_length=50)),
                ("timestamp", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "data",
                    models.JSONField(
                        blank=True,
                        default=list,
                        encoder=django.core.serializers.json.DjangoJSONEncoder,
                        help_text="The JSON response sent to Zapier.",
                    ),
                ),
                (
                    "count",
                    models.IntegerField(
                        default=0,
                        help_text="Denormalised object count, used for filtering",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="zapier_trigger_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "get_latest_by": "timestamp",
            },
        ),
    ]
