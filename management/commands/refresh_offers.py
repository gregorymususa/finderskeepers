from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from couponfinder.models import Offer, Category
from datetime import datetime, date, time, timezone

class Command(BaseCommand):
    help = 'Removes expired offers.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # handle the command
        for o in Offer.objects.filter(category=Category.objects.get(name="Travel")):
            if datetime.now(timezone.utc) > o.expiry_date:
                o.delete()
