from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from couponfinder.models import Category, Organization, Offer, Country

import requests
import sys, os
import bs4
import re
from datetime import datetime, date, time, timedelta
from random import randint
import time as builtin_time
import csv
import urllib.request, urllib.parse
import html


class WebCrawler():

    ####################
    # Helper Functions #
    ####################
    def calculate_expiry_date(self, span):
        months = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                  "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
        date_array = span.get_text().strip().replace("Ends: ", "").split(" ")

        dd = date_array[0]
        mm = months[date_array[1]]
        yyyy = date_array[2]

        return datetime(int(yyyy), mm, int(dd), 23, 59).isoformat() + 'Z'

    def calculate_expiry_warning(self, span):
        if "Expires Today".lower() == span.get_text().strip().lower():
            return datetime.combine(date.today(), time(23, 59)).isoformat()+'Z'
        diff = int(span.get_text().strip().replace("Only ", "").replace(
            " days left", "").replace(" day left", ""))
        return (datetime.combine(date.today(), time(23, 59)) + timedelta(days=diff)).isoformat()+'Z'

    def default_expiry_date(self):
        return (datetime.combine(date.today(), time(23, 59)) + timedelta(days=30)).isoformat()+'Z'

    def is_offer_exclusive(self, li):
        isExclusive = 0 < (len(li.select('div.c-offer__exclusive')))
        return isExclusive

    def get_headers(self):
        return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}

    def offer_exists(self, cat_name, extid):
        """
          Returns True, if offer exists. Otherwise, returns False.
          cat_name  — Category Name
          extid     — External Offer ID
        """
        if 0 < len(Offer.objects.filter(category=Category.objects.get(name=cat_name), external_id=extid)):
            return True
        return False

    def offer_code_is_none(self, cat_name, extid):
        """
          Returns True, if offer code is none. Otherwise, returns False.

          The aim of this function, is to correct Offer Codes, that get saved as None (e.g. due to a change in the structure of the data source).
          Fixing the way the data is obtained here, allows for overwriting of those cases.
          
          cat_name Category Name
          extid External Offer  ID
        """
        if (Offer.labels[0][1] == Offer.objects.get(category=Category.objects.get(name=cat_name),external_id=extid).label) and (None == Offer.objects.get(category=Category.objects.get(name=cat_name),external_id=extid).code):
            return True
        else:
            return False

    def requests_get_coupon_code(self, extID, cat_name):
        builtin_time.sleep(randint(45, 60))
        headers = self.get_headers()
        if "Fashion".lower() == cat_name.lower():
            r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID +
                             "?log=1&email=0&brand=&justloggedin=0&url=/fashion", headers=headers)
        elif "Travel".lower() == cat_name.lower():
            r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID +
                             "?log=1&email=0&brand=&justloggedin=0&url=/travel", headers=headers)
        elif "Experiences".lower() == cat_name.lower():
            r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID +
                             "?log=1&email=0&brand=&justloggedin=0&url=/days-out-attractions", headers=headers)
        elif "Food & Drink".lower() == cat_name.lower():
            r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID +
                             "?log=1&email=0&brand=&justloggedin=0&url=/restaurants-takeaways-bars", headers=headers)
        elif "Technology".lower() == cat_name.lower():
            r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID +
                             "?log=1&email=0&brand=&justloggedin=0&url=/technology-electrical", headers=headers)
        elif "Health".lower() == cat_name.lower():
            r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID +
                             "?log=1&email=0&brand=&justloggedin=0&url=/health-beauty", headers=headers)
        elif "Sports".lower() == cat_name.lower():
            r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID +
                             "?log=1&email=0&brand=&justloggedin=0&url=/sports-fitness-outdoors", headers=headers)
        else:
            return False

        try:
            r.raise_for_status()
        except:
            return False

        return r

    def requests_get_category(self, cat_name):
        headers = self.get_headers()
        if "Fashion".lower() == cat_name.lower():
            r = requests.get(
                'https://www.myvouchercodes.co.uk/fashion', headers=headers)
        elif "Travel".lower() == cat_name.lower():
            r = requests.get(
                'https://www.myvouchercodes.co.uk/travel', headers=headers)
        elif "Experiences".lower() == cat_name.lower():
            r = requests.get(
                'https://www.myvouchercodes.co.uk/days-out-attractions', headers=headers)
        elif "Food & Drink".lower() == cat_name.lower():
            r = requests.get(
                'https://www.myvouchercodes.co.uk/restaurants-takeaways-bars', headers=headers)
        elif "Technology".lower() == cat_name.lower():
            r = requests.get(
                'https://www.myvouchercodes.co.uk/technology-electrical', headers=headers)
        elif "Health".lower() == cat_name.lower():
            r = requests.get(
                'https://www.myvouchercodes.co.uk/health-beauty', headers=headers)
        elif "Sports".lower() == cat_name.lower():
            r = requests.get(
                'https://www.myvouchercodes.co.uk/sports-fitness-outdoors', headers=headers)
        else:
            return False

        try:
            r.raise_for_status()
        except:
            return False

        return r

    ###########
    # Getters #
    ###########

    def getOrgName(self, li):
        ps = li.select('p.c-offer__merchant-link')
        for p in ps:
            return p.get_text().replace("See all ", "").replace(" Voucher Codes", "").strip()
        return False

    def getOfferTitle(self, li, orgName):
        subject_identifiers = ["at", "with", "from", "by"]
        h2s = li.select('h2.c-offer__title')

        for h2 in h2s:
            for subject_identifier in subject_identifiers:
                target_text = " " + subject_identifier + " " + orgName
                return h2.get_text().replace(target_text, "")

        return False

    def getOfferExpiryDate(self, li):
        """
        Returns a string representation of a date, in the format: yyyy-mm-ddThh:mm:ssZ (example 2018-11-30T23:59:59Z)

        An offer has one of the following Expiry Dates. Below, is a description of how each Expiry Date type is handled
        expiry-date       - Format End Date
        expiry-warning    - Calculate End Date
        while-stocks-last - Ends in 30 days DEFAULT (to prevent eternal offers)
        [blank]           - Ends in 30 days DEFAULT (to prevent eternal offers)
        """
        expiry_states = ["span.c-offer__meta-item--expiry-date",
                         "span.c-offer__meta-item--expiry-warning", "span.c-offer__meta-item--while-stocks-last"]

        for expiry_state in expiry_states:
            spans = li.select(expiry_state)

            if [] != spans:
                span = spans[0]
                if expiry_state == expiry_states[0]:
                    return self.calculate_expiry_date(span)
                elif expiry_state == expiry_states[1]:
                    return self.calculate_expiry_warning(span)

        return self.default_expiry_date()

    def isWhileStocksLast(self, li):
        expiry_states = ["span.c-offer__meta-item--expiry-date",
                         "span.c-offer__meta-item--expiry-warning", "span.c-offer__meta-item--while-stocks-last"]

        for expiry_state in expiry_states:
            spans = li.select(expiry_state)

            if [] != spans:
                return expiry_state == expiry_states[2]

        return False

    def getOfferLabel(self, li):
        if "Voucher Code".lower() == li.select('span.c-offer__label')[0].get_text().strip().lower() or "Unique Code".lower() == li.select('span.c-offer__label')[0].get_text().strip().lower():
            return "Offer Code"
        elif "Sale".lower() == li.select('span.c-offer__label')[0].get_text().strip().lower():
            return "Sale"
        else:
            return None

    def getExternalOfferID(self, li):
        return li.get_attribute_list('data-offer-id')[0]

    def getTsandCs(self, li):
        ps = li.select('div.c-offer__terms-box-content p')
        if 0 < len(ps):
            return ps[0].get_text().strip().replace("\t", "")
        else:
            return ""

    def getSlug(self, aString):
        return aString.replace("& ", "").replace("&", "").replace("'", "").replace(".", "_").replace(" ", "_").lower()

    def getOfferCode(self, extid, cat_name):
        r = self.requests_get_coupon_code(extid, cat_name)
        if False == r:
            raise ValueError("Category could not be found!")
        soup = bs4.BeautifulSoup(r.text, "html.parser")
        offer_code_inputs = soup.select('input.c-code__text')
        if 0 < len(offer_code_inputs):
            return offer_code_inputs[0].get_attribute_list('value')[0].strip()
        else:
            print("Could not find Offer Code, for External ID %s (%s)" %
                  (extid, cat_name))
            return None

    def crawl(self, category, country):
        """
        Starts the script, with the following mandatory parameter:
        category  - "Fashion", "Travel", "Experiences", "Food & Drink", "Technology", "Health", "Sports"
        """
        r= self.requests_get_category(category)
        if False == r:
            raise ValueError("Category could not be found!")

        soup = bs4.BeautifulSoup(r.text, "html.parser")

        uls = soup.select('ul.js-offers--main')
        ul = uls[0]
        lis = ul.select('li.js-offer-container.c-offer')

        c = Category.objects.get(name=category)
        for li in lis:
            if self.is_offer_exclusive(li):
                continue

            offer_external_id = self.getExternalOfferID(li)
            if self.offer_exists(category,offer_external_id):
                if self.offer_code_is_none(category,offer_external_id):
                    offer_code = self.getOfferCode(offer_external_id,category)
                    offer_to_replace = Offer.objects.get(category=Category.objects.get(name=category),external_id=offer_external_id)
                    offer_to_replace.code = offer_code
                    offer_to_replace.save()
                    print('Replace Offer Code, for offer',offer_external_id)
                continue#skip processing, if already exists

            org_name = self.getOrgName(li)
            org_website = "http://example.com"#TODO
            org_slug = self.getSlug(org_name)
            offer_title = self.getOfferTitle(li,org_name)
            offer_expiry_date = self.getOfferExpiryDate(li)
            offer_is_while_stocks_last = self.isWhileStocksLast(li)
            offer_label = self.getOfferLabel(li)
            offer_terms = self.getTsandCs(li)
            offer_affiliate_link = "http://example.com"#TODO

            if "Offer Code" == offer_label:
                offer_code = self.getOfferCode(offer_external_id,category)
            else:
                offer_code = None

            o_tuple = Organization.objects.get_or_create(name=org_name,country=country)
            if True == o_tuple[1]:#IF created for the first time THEN setup the Org.
                o = o_tuple[0]
                o.website = org_website
                o.slug = org_slug
                o.save()
                o.category.add(c)
            else:#ELSE IF already existed THEN update the Org.
                o = o_tuple[0]
                if "http://example.com".lower() == o.website.lower():
                    o.website = org_website

                if None == o.slug:
                    o.slug = org_slug

                if [] == o.category.filter(name=category):
                    o.category.add(c)

            try:
                Offer(description=offer_title,affiliate_link=offer_affiliate_link,code=offer_code,expiry_date=offer_expiry_date,is_while_stocks_last=offer_is_while_stocks_last,label=offer_label,terms=offer_terms,external_id=offer_external_id,country=country,category=c,organization=o).save()
            except IntegrityError:#skip processing, if already exists
                continue

        return True

class AwinLoader():

    project_dir = "/home/gunter/couponfinder-env/couponfinderproject/"
    static_dir = "couponfinder/static/couponfinder/"
    collectstatic_dir = "couponfinder/logos/"

    ###############
    # Advertisers #
    ###############
    def download_advertisers(self):
        r = requests.get('https://ui2.awin.com/affiliates/shopwindow/datafeed_metadata.php?user=636515&password=ea2ca2ead39f9d99dab451eb573e0495&format=csv&filter=all_all&compression=')
        try:
            r.raise_for_status()
        except:
            print(r.status_code, '\ngoodbye!')
        
        with open(file='/var/tmp/advertisers.csv',mode='wt',encoding='utf_8') as file_writer:
            file_writer.write(r.text)
    
    def active_determ(self,active):
        return False if "no"==active.lower() else True
    
    def logo_determ(self,logo):
        return "" if "No logo provided".lower()==logo.lower() else logo
    
    def default_clickthrough_determ(self,default_clickthrough):
        return "" if "You are not joined to this merchant".lower()==default_clickthrough.lower() else default_clickthrough

    def getSlug(self, a_string):
        slug = ""
        for letter in a_string:
            if letter.isalnum():
                slug+=letter
            elif " " == letter:
                slug+="_"
        return slug.lower()
    
    def download_logo(self,external_logo,slug):
        if "" != self.logo_determ(external_logo):
            try:
                if external_logo.lower() != Organization.objects.get(slug=slug).external_logo.lower():
                    return urllib.request.urlretrieve(
                               url=external_logo,
                               filename = self.project_dir + self.static_dir + "logos/" + slug + "." + urllib.parse.urlsplit(external_logo).path.split(".")[-1])
            except:
                #throws an exception, if the Organization object does not exist
                return urllib.request.urlretrieve(
                           url=external_logo,
                           filename = self.project_dir + self.static_dir + "logos/" + slug + "." + urllib.parse.urlsplit(external_logo).path.split(".")[-1])
        return False

    def resize_logo(self,logo_path):
        """Place the logo in the middle of a white square.
        
        Keyword arguments:
        logo : string
            string path to the logo e.g. /dir/dir/file.jpg
        """
        w = int(os.popen('identify -format "%w" '+logo_path+'[0]').read())
        h = int(os.popen('identify -format "%h" '+logo_path+'[0]').read())
        x_offset = 0
        y_offset = 0
         
        if w < h:
            x_offset = (h - w)/2
            y_offset = 0
            w = h
        elif w > h:
            x_offset = 0
            y_offset = (w - h)/2
            h = w
         
        fname = logo_path.split(".",1)[0]
        ext = logo_path.split(".",1)[1]
        os.system('sudo convert -size ' + str(w) + 'x' + str(h) + ' xc:white canvas.png')
        os.system('sudo convert -coalesce canvas.png ' + logo_path  + ' -geometry +' + str(x_offset)  + '+' + str(y_offset)  +  ' -composite ' + fname + '.png')
        os.system('sudo rm -r ' + logo_path)
        os.system('sudo rm -r canvas.png')

    def read_advertisers_csv(self,f,mode,encoding):
        with open(file=f,mode=mode,encoding=encoding) as csv_file:
            csv_reader = csv.DictReader(f=csv_file)
            for row in csv_reader:
                logo_path = self.download_logo(row["Logo"],self.getSlug(row["Merchant Name"]))
                if False != logo_path:
                    logo_path = logo_path[0] 
                    self.resize_logo(logo_path)
                
                try:
                    #print(row["Merchant ID"], row["Merchant Name"])
                    slug = self.getSlug(row["Merchant Name"])
                    Organization.objects.update_or_create(
                        external_id = row["Merchant ID"],
                        source = Organization.sources[0][0],
                        defaults = {
                            'name' : html.unescape(row["Merchant Name"]),
                            'external_logo' : self.logo_determ(row["Logo"]),
                            'program_joined' : self.active_determ(row["Active"]),
                            'slogan' : html.unescape(row["Strapline"]),
                            'description' : html.unescape(row["Description"]),
                            'affiliate_link' : html.unescape(self.default_clickthrough_determ(row["Default Clickthrough"])),
                            'website' : html.unescape(row["Display URL"]),
                            'country' : Country.objects.get(iso_country_code=row["Primary Region"]),
                            'slug' : slug,
                            'logo' : "" if ""==self.logo_determ(row["Logo"]) else self.collectstatic_dir+slug+'.png'
                        }
                    )
                except:
                    # TODO: What happens if multiple sources, have the same Organization (e.g. DressLily)
                    #
                    #What happens if those Organizations have spelling variants between the sources?
                    #
                    #Can the script prompt me... with suggestions
                    #1. Choose DressLily
                    #2. Choose Lily D
                    #3. Enter Org ID
                    #
                    #-----------
                    #
                    #for now... skip entries with Integrity errors
                    #BUT list them
                    #
                    # NB. Remember advertiser duplicates, e.g. Qatar_IT, Qatar_US (there are a lot of country duplicates)
                    # possible solution: parent organization
                    #
                    #Can this happen with Offers
                    # TODO: load logos, from external logo (prefereably using media)
                    print("Integrity Error:", row["Merchant ID"], row["Merchant Name"], row["Primary Region"], row["Active"])

    def load_advertisers(self, country):
        self.download_advertisers()
        self.read_advertisers_csv(f='/var/tmp/advertisers.csv',mode='rt',encoding='utf_8')
        print('Success')

    ##############
    # Promotions #
    ##############
    def download_promotions(self,category):
        # todo download as promotions_travel.csv, promotions_fashion.csv; loading accordingly
        if "experiences"==category.lower():
            r = requests.get('https://ui.awin.com/export-promotions/636515/7f0f2cc60cbb3bee7689ed080545c2df?downloadType=csv&promotionType=&categoryIds=650,260,590,592,588,591,589&regionIds=1&advertiserIds=&membershipStatus=&promotionStatus=active')
        elif "fashion"==category.lower():
            r = requests.get('https://ui.awin.com/export-promotions/636515/7f0f2cc60cbb3bee7689ed080545c2df?downloadType=csv&promotionType=&categoryIds=147,149,170,171,548,183,179,175,172,189,194,198,206,208,204,201,542,544,546,547,595,163,168,159,169,161,167,205,613,626,623&regionIds=1&advertiserIds=&membershipStatus=&promotionStatus=active')
        elif "health"==category.lower():
            r = requests.get('https://ui.awin.com/export-promotions/636515/7f0f2cc60cbb3bee7689ed080545c2df?downloadType=csv&promotionType=&categoryIds=101,107,111,113,114,116,118&regionIds=1&advertiserIds=&membershipStatus=&promotionStatus=active')
        elif "food_drink"==category.lower():
            r = requests.get('https://ui.awin.com/export-promotions/636515/7f0f2cc60cbb3bee7689ed080545c2df?downloadType=csv&promotionType=&categoryIds=608,437,438,440,441,442,444,446,447,607&regionIds=1&advertiserIds=&membershipStatus=&promotionStatus=active')
        elif "sports"==category.lower():
            r = requests.get('https://ui.awin.com/export-promotions/636515/7f0f2cc60cbb3bee7689ed080545c2df?downloadType=csv&promotionType=&categoryIds=174,178,203,199,252,559,255,256,265,593,258,259,632,261,262,557,266,267,268,269,277,272,270,271,273,561,558,560&regionIds=1&advertiserIds=&membershipStatus=&promotionStatus=active')
        elif "technology"==category.lower():
            r = requests.get('https://ui.awin.com/export-promotions/636515/7f0f2cc60cbb3bee7689ed080545c2df?downloadType=csv&promotionType=&categoryIds=80,83,84,85,86,87,88,90,89,91,60,128,130,133,212,209,210,211,220,228,229,11,537,19,22,24,30,29,32,619,34,652,45,46,651,47,48,49,44,50,51,231,549,576,575,577,579,354,353,350,351,352&regionIds=1&advertiserIds=&membershipStatus=&promotionStatus=active')
        elif "travel"==category.lower():
            r = requests.get('https://ui.awin.com/export-promotions/636515/7f0f2cc60cbb3bee7689ed080545c2df?downloadType=csv&promotionType=&categoryIds=629,329,330,333,335,336,338&regionIds=1&advertiserIds=&membershipStatus=&promotionStatus=active')

        try:
            r.raise_for_status()
        except:
            print(r.status_code, '\ngoodbye!')
        
        with open(file='/var/tmp/promotions_'+category+'.csv',mode='wt',encoding='utf_8') as file_writer:
            file_writer.write(r.text)

    def type_determ(self, typ):
        if "Promotions Only" == typ:
            return Offer.labels[1][1]
        elif "Vouchers Only" == typ:
            return Offer.labels[0][1]

    def code_determ(self, typ, code):
        if "Promotions Only" == typ:
            return ""
        elif "Vouchers Only" == typ:
            return code

    def starts_determ(self, starts):
        # e.g. 31/07/2019 16:36:00
        dd = starts[0:2]
        mm = starts[3:5]
        yyyy = starts[6:11]
        HH = starts[11:13]
        MM = starts[14:16]
        SS = starts[17:19]
        return datetime.combine(
            date(year=int(yyyy), month=int(mm), day=int(dd)),
            time(hour=int(HH),minute=int(MM), second=int(SS))
        ).isoformat()+'Z'

    def ends_determ(self, ends):
        # e.g. 30/09/2019 22:59:00
        dd = ends[0:2]
        mm = ends[3:5]
        yyyy = ends[6:11]
        HH = ends[11:13]
        MM = ends[14:16]
        SS = ends[17:19]
        return datetime.combine(
            date(year=int(yyyy), month=int(mm), day=int(dd)),
            time(hour=int(HH),minute=int(MM), second=int(SS))
        ).isoformat()+'Z'

    def exclusive_determ(self, exclusive):
        return True if "true"==exclusive.lower() else False

    def read_promotions_csv(self,f,mode,encoding,category,country):
        with open(file=f,mode=mode,encoding=encoding) as csv_file:
            csv_reader = csv.DictReader(f=csv_file)
            for row in csv_reader:
                if "United Kingdom" in row["Regions"] and "Promotions Only" == row["Type"]:
                    # load GB only because we are not ready for other countries (in terms of legal requirements)
                    # load promotions only, because current vouchers are ***** (asked AWIN how to proceed)
                    # TODO stop hardcoding the above
                    #print(row['Advertiser'],row['Advertiser ID'],row['Terms'])#promotions
                    try:
                        Offer.objects.update_or_create(
                            external_id = row["Promotion ID"],
                            source = Offer.sources[0][0],
                            defaults = {
                                'organization' : Organization.objects.get(external_id=row['Advertiser ID']),
                                'label' : self.type_determ(row["Type"]),
                                'code' : self.code_determ(row["Type"], row["Code"]),
                                'title' : html.unescape(row["Title"]),
                                'description' : html.unescape(row["Description"]),
                                'start_date' : self.starts_determ(row["Starts"]),
                                'expiry_date' : self.ends_determ(row["Ends"]),
                                'category' : Category.objects.get(slug=category),
                                'country' : Country.objects.get(iso_country_code=country),
                                'terms' : row["Terms"],
                                'affiliate_link' : html.unescape(row["Deeplink Tracking"]),
                                'link' : html.unescape(row["Deeplink"]),
                                'exclusive' : self.exclusive_determ(row["Exclusive"])
                            }
                        )
                    except Exception as e:
                        print(row['Advertiser'],row['Advertiser ID'],e)
                    
 
    def load_promotions(self, category, country):
        self.download_promotions(category)
        self.read_promotions_csv(f='/var/tmp/promotions_'+category+'.csv',mode='rt',encoding='utf_8', category=category, country=country)
        print('Success')


class Command(BaseCommand):
    help = 'args method | category'

    def add_arguments(self, parser):
        parser.add_argument('method', nargs=1, choices=['crawler', 'awin'])
        parser.add_argument('target', nargs=1, choices=['advertisers', 'promotions'])
        parser.add_argument('country', nargs=1, choices=list(Country.target_country_codes))
        parser.add_argument('category', nargs=1, choices=[
                            'experiences', 'fashion', 'health', 'food_drink', 'sports', 'technology', 'travel'])

    def handle(self, *args, **options):
        # handle the command
        
        if "crawler" == options['method'][0].lower():
            crawler = WebCrawler()
            crawler.crawl(options['category'][0],Country.objects.get(iso_country_code=options['country'][0]))
        elif "awin" == options['method'][0].lower() and 'advertisers' == options['target'][0].lower():
            awin_loader = AwinLoader()
            awin_loader.load_advertisers(Country.objects.get(iso_country_code=options['country'][0]))
        elif "awin" == options['method'][0].lower() and 'promotions' == options['target'][0].lower():
            awin_loader = AwinLoader()
            awin_loader.load_promotions(options['category'][0], options['country'][0])
        
        # We might need to write the MAIN logic in here, and define the helper functions, elsewhere in the class -- makes it easier to use the Query Set API
