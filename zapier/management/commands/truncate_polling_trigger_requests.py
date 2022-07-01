from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytz
from django.core.management.base import BaseCommand, CommandParser
from django.utils.timezone import now as tz_now

from zapier.models import PollingTriggerRequest


class Command(BaseCommand):
    help = "Truncates the request log table."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--interval",
            default=7,
            type=int,
            help="Number of days after which to delete log entries.",
        )
        parser.add_argument(
            "--max",
            default=10000,
            type=int,
            help="Max number of records to keep (truncate to this number).",
        )

    def get_max_timestamp(self, max_count: int) -> datetime:
        """Return the timestamp of the nth item."""
        timestamps = PollingTriggerRequest.objects.order_by("-timestamp").values_list(
            "timestamp", flat=True
        )[:max_count]
        return timestamps[-1] if timestamps else pytz.utc.localize(datetime.max)

    def get_cut_off(self, interval: int, max_count: int) -> datetime:
        """Return datetime based on interval or count, whichever is sooner."""
        return min(
            tz_now() - timedelta(days=interval),
            self.get_max_timestamp(max_count),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        interval = options["interval"]
        max_count = options["max"]
        self.stdout.write("Truncating PollingTriggerRequest logs:")
        self.stdout.write(f" - Interval: {interval} days")
        self.stdout.write(f" - Max:      {max_count} records")
        cut_off = self.get_cut_off(options["interval"], options["max"])
        self.stdout.write(f" - Cut-off:  {cut_off}")
        qs = PollingTriggerRequest.objects.filter(timestamp__lt=cut_off)
        deleted, _ = qs.delete()
        self.stdout.write(f"---\nDeleted {deleted} records.")
