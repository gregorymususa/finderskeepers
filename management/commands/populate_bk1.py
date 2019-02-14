from django.core.management.base import BaseCommand, CommandError
from couponfinder.models import Category, Organization, Offer

import requests
import sys
import bs4
import re
from datetime import datetime, date, time, timedelta
from random import randint
import time as builtin_time


class WebCrawler():
    
    ####################
    # Helper Functions #
    ####################
    def calculate_expiry_date(span):
	months = {"January":1, "February":2, "March":3, "April":4, "May":5, "June":6, "July":7, "August":8, "September":9, "October":10, "November":11, "December":12}
	date_array = span.get_text().strip().replace("Ends: ","").split(" ")

	dd = date_array[0]
	mm = months[date_array[1]]
	yyyy = date_array[2]

	return datetime(int(yyyy),mm,int(dd),23,59).isoformat() + 'Z'


    def calculate_expiry_warning(span):
	if "Expires Today" == span.get_text().strip():
	     return datetime.combine(date.today(),time(23,59)).isoformat()+'Z'
	diff = int(span.get_text().strip().replace("Only ","").replace(" days left","").replace(" day left",""))
	return ( datetime.combine(date.today(),time(23,59)) + timedelta(days=diff) ).isoformat()+'Z'


    def default_expiry_date():
	return ( datetime.combine(date.today(),time(23,59)) + timedelta(days=30) ).isoformat()+'Z'


    def is_offer_exclusive(li):
	isExclusive = 0 < (len(li.select('div.c-offer__exclusive')))
	return isExclusive


    def get_headers():
	return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'}


    def offer_exists(cat_name,extid):
	"""
	  Returns True, if offer exists. Otherwise, returns False.
	  cat_name  — Category Name
	  extid     — External Offer ID
	"""
	if 0 < len(Offer.objects.filter(category=Category.objects.get(name=cat_name),external_id=extid)):
	    return True
	return False


    def requests_get_coupon_code(extID,cat_name):
	builtin_time.sleep(randint(45,60))
	headers = get_headers()
	if "Fashion" == cat_name:
	    r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID + "?log=1&email=0&brand=&justloggedin=0&url=/fashion",headers=headers)
	elif "Travel" == cat_name:
	    r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID + "?log=1&email=0&brand=&justloggedin=0&url=/travel",headers=headers)
	elif "Experiences" == cat_name:
	    r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID + "?log=1&email=0&brand=&justloggedin=0&url=/days-out-attractions",headers=headers)
	elif "Restaurants" == cat_name:
	    r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID + "?log=1&email=0&brand=&justloggedin=0&url=/restaurants-takeaways-bars",headers=headers)
	elif "Technology" == cat_name:
	    r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID + "?log=1&email=0&brand=&justloggedin=0&url=/technology-electrical",headers=headers)
	elif "Groceries" == cat_name:
	    r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID + "?log=1&email=0&brand=&justloggedin=0&url=/food-drink",headers=headers)
	elif "Sports" == cat_name:
	    r = requests.get("https://www.myvouchercodes.co.uk/system/reveal/" + extID + "?log=1&email=0&brand=&justloggedin=0&url=/sports-fitness-outdoors",headers=headers)
	else:
	    return False
	
	try:
	    r.raise_for_status()
	except:
	    return False
	
	return r


    def requests_get_category(cat_name):
	headers = get_headers()
	if "Fashion" == cat_name:
	    r = requests.get('https://www.myvouchercodes.co.uk/fashion',headers=headers)
	elif "Travel" == cat_name:
	    r = requests.get('https://www.myvouchercodes.co.uk/travel',headers=headers)
	elif "Experiences" == cat_name:
	    r = requests.get('https://www.myvouchercodes.co.uk/days-out-attractions',headers=headers)
	elif "Restaurants" == cat_name:
	    r = requests.get('https://www.myvouchercodes.co.uk/restaurants-takeaways-bars',headers=headers)
	elif "Technology" == cat_name:
	    r = requests.get('https://www.myvouchercodes.co.uk/technology-electrical',headers=headers)
	elif "Groceries" == cat_name:
	    r = requests.get('https://www.myvouchercodes.co.uk/food-drink',headers=headers)
	elif "Sports" == cat_name:
	    r = requests.get('https://www.myvouchercodes.co.uk/sports-fitness-outdoors',headers=headers)
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
    def getOrgName(li):
	ps = li.select('p.c-offer__merchant-link')
	for p in ps:
	    return p.get_text().replace("See all ","").replace(" Voucher Codes","").strip()
	return False


    def getOfferTitle(li,orgName):
	subject_identifiers = ["at","with","from","by"]
	h2s = li.select('h2.c-offer__title')

	for h2 in h2s:
	    for subject_identifier in subject_identifiers:
		target_text = " " + subject_identifier + " " + orgName
		return h2.get_text().replace(target_text,"")

	return False


    def getOfferExpiryDate(li):
	"""
	Returns a string representation of a date, in the format: yyyy-mm-ddThh:mm:ssZ (example 2018-11-30T23:59:59Z)

	An offer has one of the following Expiry Dates. Below, is a description of how each Expiry Date type is handled
	expiry-date       - Format End Date
	expiry-warning    - Calculate End Date
	while-stocks-last - Ends in 30 days DEFAULT (to prevent eternal offers)
	[blank]           - Ends in 30 days DEFAULT (to prevent eternal offers)
	"""
	expiry_states = ["span.c-offer__meta-item--expiry-date","span.c-offer__meta-item--expiry-warning","span.c-offer__meta-item--while-stocks-last"]
	
	for expiry_state in expiry_states:
	    spans = li.select(expiry_state)
	    
	    if [] != spans:
		span = spans[0]
		if expiry_state == expiry_states[0]:
		    return calculate_expiry_date(span)
		elif expiry_state == expiry_states[1]:
		    return calculate_expiry_warning(span)
		
	return default_expiry_date()


    def isWhileStocksLast(li):
	expiry_states = ["span.c-offer__meta-item--expiry-date","span.c-offer__meta-item--expiry-warning","span.c-offer__meta-item--while-stocks-last"]
	
	for expiry_state in expiry_states:
	    spans = li.select(expiry_state)
	    
	    if [] != spans:
		return expiry_state == expiry_states[2]

	return False


    def getOfferLabel(li):
	if "Voucher Code" == li.select('span.c-offer__label')[0].get_text().strip() or "Unique Code" == li.select('span.c-offer__label')[0].get_text().strip():
	    return "Offer Code"
	elif "Sale" == li.select('span.c-offer__label')[0].get_text().strip():
	    return "Sale"
	else:
	    return None


    def getExternalOfferID(li):
	return li.get_attribute_list('data-offer-id')[0]


    def getTsandCs(li):
	ps = li.select('div.c-offer__terms-box-content p')
	if 0 < len(ps):
	    return ps[0].get_text().strip().replace("\t","")
	else:
	    return ""


    def getSlug(aString):
	return aString.replace("& ","").replace("&","").replace("'","").replace(".","_").replace(" ","_").lower()


    def getOfferCode(extid,cat_name):
	r = requests_get_coupon_code(extid,cat_name)
	soup = bs4.BeautifulSoup(r.text, "html.parser")
	offer_code_spans = soup.select('span.c-code__text')
	if 0 < len(offer_code_spans):
	    return offer_code_spans[0].get_text().strip()
	else:
	    print("Could not find Offer Code, for External ID %s (%s)" % (extid,cat_name))
	    return None


    def crawl(self,target_category):
        print("Hello, I am a custom command!")
        print(target_category)



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
        crawler.crawl(options['category'][0])


        #We might need to write the MAIN logic in here, and define the helper functions, elsewhere in the class -- makes it easier to use the Query Set API
