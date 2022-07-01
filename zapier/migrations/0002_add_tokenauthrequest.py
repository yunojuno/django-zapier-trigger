# Generated by Django 4.0.2 on 2022-07-01 18:01

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zapier", "0001_initial"),
    ]

    operations = [
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
                        to="zapier.zapiertoken",
                    ),
                ),
            ],
            options={
                "get_latest_by": "timestamp",
            },
        ),
    ]