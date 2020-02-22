from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from couponfinder.models import Category, Organization, Offer, Country
from couponfinderqa.models import StaffPreferences, ImportedOffer

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
            return p.get_text().replace("See all ", "").replace(" Voucher Codes", "").replace(" Discount &", "").strip()
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
        if "Voucher Code".lower() == li.select('span.c-offer__label')[0].get_text().strip().lower() or "Discount Code".lower() == li.select('span.c-offer__label')[0].get_text().strip().lower() or "Unique Code".lower() == li.select('span.c-offer__label')[0].get_text().strip().lower():
            return "Offer Code"
        elif "Sale".lower() == li.select('span.c-offer__label')[0].get_text().strip().lower():
            return "Sale"
        elif "Deal".lower() == li.select('span.c-offer__label')[0].get_text().strip().lower():
            return "Deal"
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
            #print("Could not find Offer Code, for External ID %s (%s)" %
            #      (extid, cat_name))
            return None

    def crawl(self, category, country, silent_mode):
        """
        Starts the script, with the following mandatory parameter (representing Category.name):
        category - 'experiences', 'fashion', 'health', 'food & drink', 'sports', 'technology', 'travel'
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
            org_name = self.getOrgName(li)
            org_slug = self.getSlug(org_name)
            offer_title = self.getOfferTitle(li,org_name)
            offer_expiry_date = self.getOfferExpiryDate(li)
            offer_is_while_stocks_last = self.isWhileStocksLast(li)
            offer_label = self.getOfferLabel(li)
            offer_terms = self.getTsandCs(li)

            if "Offer Code" == offer_label:
                offer_code = self.getOfferCode(offer_external_id,category)
            else:
                offer_code = None

            if offer_label == 'Offer Code':
                ImportedOffer.objects.update_or_create(
                    cat_name = c.name,
                    org_name = org_name,
                    iso_country_code = country.iso_country_code,
                    offer_code = offer_code,
                    defaults = {
                        'offer_title' : offer_title,
                        'offer_expiry_date' : offer_expiry_date,
                        'offer_is_while_stocks_last' : offer_is_while_stocks_last,
                        'offer_label' : offer_label,
                        'offer_terms' : offer_terms,
                        'offer_source' : ImportedOffer.C_MVC
                    }
                )
                
                if not silent_mode:
                    print(
                        c.name,
                        org_name,
                        offer_title,
                        offer_code,
                        offer_expiry_date,
                        offer_is_while_stocks_last,
                        offer_label,
                        offer_terms,
                        offer_external_id,
                        country.iso_country_code,
                        sep=","
                    )
        
        return True


class Command(BaseCommand):
    help = 'args method | category'

    def add_arguments(self, parser):
        parser.add_argument('country', nargs=1, choices=list(Country.target_country_codes))
        parser.add_argument('category', nargs='?', choices=[
                            'experiences', 'fashion', 'health', 'food & drink', 'sports', 'technology', 'travel'], default=None)
        parser.add_argument('-s', action='store_true')

    def handle(self, *args, **options):
        # handle the command
        
        crawler = WebCrawler()
        crawler.crawl(options['category'],Country.objects.get(iso_country_code=options['country'][0]),options['s'])
