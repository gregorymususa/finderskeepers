from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from couponfinder.models import Offer
from datetime import datetime
import pytz

class Command(BaseCommand):
    help = 'Removes expired offers.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # handle the command
        Offer.objects.filter(expiry_date__lt=datetime.now(pytz.utc)).delete()
