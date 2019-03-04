from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from couponfinder.models import Organization
import configparser
import os


class Command(BaseCommand):
    help = 'Resizes logos. Takes an array of logo paths.'

    def file_exists(self, org_logo):
        return True


    def add_arguments(self, parser):
        parser.add_argument('logo_paths', nargs='*')


    def handle(self, *args, **options):
        config = configparser.ConfigParser()
        config.read("config.ini")

        # handle the command
        for logo_path in options['logo_paths']:
            w = int(os.popen('identify -format "%w" '+logo_path).read())
            h = int(os.popen('identify -format "%h" '+logo_path).read())
            x_offset = 0
            y_offset = 0

            if w < h:
                x_offset = (h - w)/2
                y_offset = 0
                w = h
            elif w >= h:
                x_offset = 0
                y_offset = (w - h)/2
                h = w

            fname = logo_path.split(".",1)[0]
            ext = logo_path.split(".",1)[1]
            os.system('sudo convert -size ' + str(w) + 'x' + str(h) + ' xc:white canvas.png')
            os.system('sudo convert canvas.png ' + logo_path  + ' -geometry +' + str(x_offset)  + '+' + str(y_offset)  +  ' -composite ' + fname + '.png')
