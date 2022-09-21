# Generated by Django 4.1 on 2022-09-14 18:15

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zapier_triggers", "0002_triggersubscription_zap_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="triggerevent",
            name="object_count",
            field=models.IntegerField(
                default=0, help_text="The count of objects stored in the event_data."
            ),
        ),
        migrations.AddField(
            model_name="triggerevent",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, help_text="Public ID used for tracking purposes."
            ),
        ),
    ]
