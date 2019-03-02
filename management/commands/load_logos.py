from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from couponfinder.models import Category, Organization, Offer




class Command(BaseCommand):
    help = 'Loads logo file path, to Organization.logo if file exists. Takes an array of Organization.slugs, as an argument'

    def file_exists(self, org_logo):
        return True


    def add_arguments(self, parser):
        parser.add_argument('org_slugs', nargs='*')


    def handle(self, *args, **options):
        # handle the command
        for org_slug in options['org_slugs']:
            if 0 < len(Organization.objects.filter(slug=org_slug)):
                o = Organization.objects.filter(slug=org_slug)[0]
                o.logo = "couponfinder/logos/" + org_slug + ".png"
                if self.file_exists(o.logo):
                    o.save()
                else:
                    print("File doesn't exist!")
