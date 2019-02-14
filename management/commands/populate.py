from django.core.management.base import BaseCommand, CommandError
from couponfinder.models import Category, Organization, Offer

class WebCrawler():
    def crawl(self,target_category):
        print("Hello, I am a custom command!")


class Command(BaseCommand):
    help = 'args method | category'

    def add_arguments(self, parser):
        parser.add_argument('method', nargs=1, choices=['crawler','provider'])
        parser.add_argument('category', nargs=1, choices=['experiences','fashion','groceries','restaurants','sports','technology','travel'])

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
        crawler = WebCrawler()
        crawler.crawl("Education")


        #We might need to write the MAIN logic in here, and define the helper functions, elsewhere in the class -- makes it easier to use the Query Set API
