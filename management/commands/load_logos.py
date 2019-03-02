from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from couponfinder.models import Category, Organization, Offer
import requests
import configparser


class Command(BaseCommand):
    help = 'Loads logo file path, to Organization.logo if file exists. Takes an array of Organization.slugs, as an argument'

    def file_exists(self, org_logo):
        config = configparser.ConfigParser()
        config.read("config.ini")
        org_logo_url = "http://"+config['environment']['host']+"/static/"+org_logo

        r = requests.head(org_logo_url)
        
        if 200 == int(r.status_code):
            return True
        else:
            return False


    def add_arguments(self, parser):
        parser.add_argument('org_slugs', nargs='*')


    def handle(self, *args, **options):
        config = configparser.ConfigParser()
        config.read("config.ini")

        # handle the command
        for org_slug in options['org_slugs']:
            if 0 < len(Organization.objects.filter(slug=org_slug)):
                o = Organization.objects.filter(slug=org_slug)[0]
                o.logo = "couponfinder/logos/" + org_slug + config['environment']['image_format']
                if self.file_exists(o.logo):
                    o.save()
                else:
                    print(org_slug+config['environment']['image_format'],"doesn't exist!")
