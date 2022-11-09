import sys

# import requests
from django.core.management.base import BaseCommand

# import time
# from datetime import date


# from django.db.models import Max

# from count_history_v2.base.models import Parameter
# from count_history_v2.notable_humans.models import (
#     Human,
#     Lifedate,
#     Nonhuman,
#     Update,
#     Wikidata,
#     Wikipedia,
# )


class Command(BaseCommand):
    help = "This gets an update for all human QIDs by the end of every week."
    max_days_between_updates = 0
    log_id = "get_human_wikidata: "
    sleep_time = 3
    requests_user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0"
    )

    def custom_print(self, message, style):
        if style == "SUCCESS":
            self.stdout.write(self.style.SUCCESS(f"{self.log_id}{message}"))
        elif style == "OKBLUE":
            self.stdout.write(self.style.MIGRATE_HEADING(f"{self.log_id}{message}"))
        elif style == "WARNING":
            self.stdout.write(self.style.WARNING(f"{self.log_id}{message}"))
        elif style == "ERROR":
            self.stdout.write(self.style.ERROR(f"{self.log_id}{message}"))
        sys.stdout.flush()

    def add_arguments(self, parser):
        parser.add_argument("args", nargs="+", type=str)

    def handle(self, *args, **options):
        self.custom_print(f"{self.log_id}: Starting up...", "OKBLUE")
        self.custom_print(f"{self.log_id}: {args}", "OKBLUE")
