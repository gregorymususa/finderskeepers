from django.core.management.base import BaseCommand, CommandError
from couponfinder.models import Category, Organization, Offer

class Command(BaseCommand):
    help = 'args method | category'

    def add_arguments(self, parser):
        parser.add_argument('method')
        parser.add_argument('category')

    def handle(self, *args, **options):
        #handle the command
        #Add a Class WebCrawler - then call Class.main(category)
        #Add a Class WebCrawler, and import - then call Class.main(category)
        #
        #IF method == Crawler  - then call WebCrawler.main(category)
        #IF method == Provider - then call Provider.main(category)
        #
        #Need to practice python Classes. Writing and calling them.
        #What happens if the Classes are in the same .py file / what happens if I have to import them, what does it take / what file structure does it take
        print("Hello, I am a custom command!")


        #We might need to write the MAIN logic in here, and define the helper functions, elsewhere in the class -- makes it easier to use the Query Set API
