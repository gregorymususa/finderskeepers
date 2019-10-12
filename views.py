from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.template import Template, context, loader
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Category, Organization, Offer, Country

import json, os, requests
from datetime import datetime, date
import ast

# Query Set Reference:      https://docs.djangoproject.com/en/2.1/ref/models/querysets/

#####################
# Utility Functions #
#####################
"""
Dynamically returns an absolute path, to a file (absolute from the current user's home dir);
when given the file's relative path.

relative_path - [Char] Relative path to the file; from the folder that this script, is currently in. Example: "templates/couponfinder/css/styles.css"
"""
def get_file_path(relative_path):
    curr_dir = os.path.dirname(__file__)
    rel_path = relative_path 
    file_path = os.path.join(curr_dir,rel_path)
    return file_path

def write_to_file(filename, content):
    """
    Writes content to a file; the file is in directory /var/tmp
    -----------------------------------------------------------
    Parameters
        filename : str
            e.g. variable_value.txt
        content : str
            e.g. 'the value of a variable, that is being investigated'
    """
    with open(file='/var/tmp/'+filename,mode='wt',encoding='utf_8') as file_writer:
        file_writer.write(content)

def get_all_categories():
    return Category.objects.order_by('manual_rank')


def get_footer_categories():
    return Category.objects.order_by('manual_rank')[0:3]


def get_addt_footer_categories():
    return Category.objects.order_by('manual_rank')[3:7]


def get_visitor_country(visitor_ip):
    """
    Returns two-digit ISO Country Code, where the supplied IP address is located
    ----------------------------------------------------------------------------
    Parameters
      visitor_ip : str
    """
    api_key = str(os.getenv('IPDB_API_KEY'))
    output_format = 'json'
    r = requests.get("http://api.ipinfodb.com/v3/ip-city/?" + "ip=" + str(visitor_ip)  + "&key=" + str(api_key) + "&format=" + str(output_format))
 
    try:
        if None == r.raise_for_status():
            output_json = json.loads(r.text)
            country_code = output_json['countryCode']
            return country_code
        else:
            return "False"
    except:
        return "trace" 


def get_country(iso_country_code):
    """
    Returns Country object (from Models.py), corresponding to the supplied two-digi iso_country_code
    ---------------------------------------------------------------------------------------------
    iso_country_code : str (two-digit iso code)
    """
    try:
        f = Country.objects.get(iso_country_code=iso_country_code)
    except:
        return Country.objects.get(iso_country_code=Country.default_country_code)
    return f


def get_location(request):
    """
    Returns a cookie and a country object, containing the Visitor's location.
    If the Visitor requests a new location - Returns the Visitor's new location.
    
    If a Cookie does not exists, and the Visitor has not requested a new location / or if the Cookie has been tampered with - Returns the Visitor's IP based location
    """
    try:
        if "POST" == request.method:
            visitor_country_code = request.POST['location-choice']
            country = get_country(visitor_country_code)
        else:
            visitor_country_code = request.get_signed_cookie(key=os.environ['COUPONFINDER_COOKIE_KEY_LOCATION'], salt=os.environ['COUPONFINDER_SIGNED_COOKIE_SALT'],
                                                             max_age=31536000)
            country = get_country(visitor_country_code)
    except:
        visitor_country_code = get_visitor_country(request.META['REMOTE_ADDR'])
        country = get_country(visitor_country_code)

    if visitor_country_code in Country.target_country_codes:
        return {'visitor_country_code':visitor_country_code,'country':country}
    else:
        visitor_country_code = Country.default_country_code
        country = get_country(visitor_country_code)
        return {'visitor_country_code':visitor_country_code,'country':country}


def save_signed_cookie(request, response, consent_mode, key, value, secure_cookie=True, http_only=True, max_age=31536000):
    allowed_consent_modes = ('preferences','statistics','marketing')
    
    if consent_mode in allowed_consent_modes:
        try:
            original_string = request.COOKIES['CookieConsent']
            string_dict = original_string.replace("%2C",",'").replace(":","':").replace("{","{'").replace("true","True").replace("false","False")
            cookie_consent = ast.literal_eval(string_dict)
            
            if cookie_consent[consent_mode]:
                response.set_signed_cookie(key=key, value=value, salt=os.environ['COUPONFINDER_SIGNED_COOKIE_SALT'],
                                           secure=secure_cookie, httponly=http_only, max_age=max_age, domain='discount-ted.com', path='/')
            return True
        except:
            # set necessary cookies only; user has not accepted cookies
            return False
    else:
        return False


def diff(list1, list2):
    list2 = set(list2)
    return [list3 for list3 in list1 if list3 not in list2]


#############################################################################################
# Output Functions                                                                          #
#                                                                                           #
# All "Template Rendering" Views, need to have the following functions called at the start: #
#    categories = get_all_categories()                                                      #
#    footer_categories = get_footer_categories()                                            #
#    addt_footer_categories = get_addt_footer_categories()                                  #
#    location = get_location(request)                                                       #
#    visitor_country_code = location['visitor_country_code']                                #
#    country = location['country']                                                          #
#    countries = Country.objects.filter(iso_country_code__in = Country.target_country_codes)#
#                                                                                           #
# Because base.html uses the data from these results                                        #
#############################################################################################

def index(request):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    location = get_location(request)
    visitor_country_code = location['visitor_country_code']
    country = location['country']
    countries = Country.objects.filter(iso_country_code__in = Country.target_country_codes)
    
    country_alert = False
    if Country.default_country_code.lower() == visitor_country_code.lower():
        write_to_file('variable_peek.txt',visitor_country_code.lower())
        country_alert = 'Apologies, we do not currently serve your region!'

    organizations = Organization.objects.all()
    excluded_orgs = Organization.objects.filter(exclude=True, country=Country.objects.get(iso_country_code=visitor_country_code))

    now = datetime.utcnow()

    # TODO select the homepage offers based on impressions / conversion rates

    ##################
    # Small Displays #
    ##################
    sm_offer_range = Offer.objects.none()
    sm_offers = []
    for catg in Category.objects.all():
        sm_offers.append(
            Offer.objects.filter(
                ~Q(organization__in=excluded_orgs),
                category=Category.objects.get(name=catg.name),
                country=Country.objects.get(iso_country_code=visitor_country_code),
                organization__in=Organization.objects.filter(country=Country.objects.get(iso_country_code=visitor_country_code)),
                expiry_date__gt=now,
                exclude=False).order_by('?')[0:4])
    
    sm_offer_range = sm_offer_range.union(sm_offers[0],sm_offers[1],sm_offers[2],sm_offers[3],sm_offers[4],sm_offers[5],sm_offers[6])

    ##################
    # Large Displays #
    ##################
    lg_offer_range = Offer.objects.none()
    lg_offers = []
    for catg in Category.objects.all():
        lg_offers.append(
            Offer.objects.filter(
                ~Q(organization__in=excluded_orgs),
                category=Category.objects.get(name=catg.name),
                country=Country.objects.get(iso_country_code=visitor_country_code),
                organization__in=Organization.objects.filter(country=Country.objects.get(iso_country_code=visitor_country_code)),
                expiry_date__gt=now,
                exclude=False).order_by('?')[0:9])
    lg_offer_range = lg_offer_range.union(lg_offers[0],lg_offers[1],lg_offers[2],lg_offers[3],lg_offers[4],lg_offers[5],lg_offers[6])

    context = {'categories': categories, 'organizations': organizations, 'current_visitor_country_code': visitor_country_code,
               'active_country': country, 'countries': countries, 'default_country_code': Country.default_country_code,
               'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories, 'alert': country_alert,
               'sm_offer_range': sm_offer_range, 'lg_offer_range': lg_offer_range}
    template = loader.get_template('couponfinder/index.html')
    r = HttpResponse(template.render(context, request))
    save_signed_cookie(request, r, 'preferences', os.environ['COUPONFINDER_COOKIE_KEY_LOCATION'], visitor_country_code)
    return r


def category(request, category_name_slug):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    location = get_location(request)
    visitor_country_code = location['visitor_country_code']
    excluded_orgs = Organization.objects.filter(exclude=True, country=Country.objects.get(iso_country_code=visitor_country_code))

    country = location['country']
    countries = Country.objects.filter(iso_country_code__in = Country.target_country_codes)
    country_alert = False
    if Country.default_country_code.lower() == visitor_country_code.lower():
        country_alert = 'Apologies, we do not currently serve your region!'

    now = datetime.utcnow()

    page = request.GET.get("page",False)
    if page != False:
        offers = Paginator(Offer.objects.filter(~Q(organization__in=excluded_orgs),
                                                category=Category.objects.filter(slug=category_name_slug)[0],
                                                country=Country.objects.get(iso_country_code=visitor_country_code),
                                                organization__in=Organization.objects.filter(country=Country.objects.get(iso_country_code=visitor_country_code)),
                                                expiry_date__gt=now),15).page(page)
    else:
        offers = Paginator(Offer.objects.filter(~Q(organization__in=excluded_orgs),
                                                category=Category.objects.filter(slug=category_name_slug)[0],
                                                country=Country.objects.get(iso_country_code=visitor_country_code),
                                                organization__in=Organization.objects.filter(country=Country.objects.get(iso_country_code=visitor_country_code)),
                                                expiry_date__gt=now),15).page(1)

    category = Category.objects.filter(slug=category_name_slug)[0]

    context = {'categories': categories, 'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories, 'alert': country_alert,
               'offers': offers, 'category': category, 'current_visitor_country_code': visitor_country_code, 'active_country': country, 'countries': countries,
               'default_country_code': Country.default_country_code}
    template = loader.get_template('couponfinder/category.html')
    r = HttpResponse(template.render(context, request))
    save_signed_cookie(request, r, 'preferences', os.environ['COUPONFINDER_COOKIE_KEY_LOCATION'], visitor_country_code)
    return r


def ajax_category(request, category_name_slug):
    page = request.GET.get("page",False)
    media = request.GET.get("media", False)
 
    now = datetime.utcnow()

    visitor_country_code = get_location(request)['visitor_country_code']
    excluded_orgs = Organization.objects.filter(exclude=True, country=Country.objects.get(iso_country_code=visitor_country_code))
    if page != False:
        offers = Paginator(Offer.objects.filter(~Q(organization__in=excluded_orgs),
                                                category=Category.objects.filter(slug=category_name_slug)[0],
                                                country=Country.objects.get(iso_country_code=visitor_country_code),
                                                organization__in=Organization.objects.filter(country=Country.objects.get(iso_country_code=visitor_country_code)),
                                                expiry_date__gt=now),15).page(page)

    context = {'offers': offers}

    if "lg" == media:
        template = loader.get_template('couponfinder/offer-lg.html')
    elif "sm" == media:
        template = loader.get_template('couponfinder/offer-sm-md.html')
    
    return HttpResponse(template.render(context, request))


def business(request, business_name_slug):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    location = get_location(request)
    visitor_country_code = location['visitor_country_code']
    country = location['country']
    countries = Country.objects.filter(iso_country_code__in = Country.target_country_codes)
    country_alert = False
    if Country.default_country_code.lower() == visitor_country_code.lower():
        country_alert = 'Apologies, we do not currently serve your region!'

    now = datetime.utcnow()

    organization = Organization.objects.get(slug=business_name_slug,
                                            country=Country.objects.get(iso_country_code=visitor_country_code),
                                            exclude=False)

    offers = Offer.objects.filter(organization=organization,
                                  country=Country.objects.get(iso_country_code=visitor_country_code),
                                  expiry_date__gt=now)
    
    context = {'categories': categories, 'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories, 'alert': country_alert,
               'business_name_slug': business_name_slug, 'organization': organization, 'offers': offers, 'current_visitor_country_code': visitor_country_code,
               'active_country': country, 'countries': countries, 'default_country_code': Country.default_country_code}
    template = loader.get_template('couponfinder/business.html')
    r = HttpResponse(template.render(context, request))
    save_signed_cookie(request, r, 'preferences', os.environ['COUPONFINDER_COOKIE_KEY_LOCATION'], visitor_country_code)
    return r


def search(request):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    location = get_location(request)
    visitor_country_code = location['visitor_country_code']
    country = location['country']
    countries = Country.objects.filter(iso_country_code__in = Country.target_country_codes)
    country_alert = False
    if Country.default_country_code.lower() == visitor_country_code.lower():
        country_alert = 'Apologies, we do not currently serve your region!'

    search_term = request.GET['business_name'].strip()
    search_term_keywords = search_term.split(" ")

    organizations = Organization.objects.filter(name__icontains=search_term,
                                                country=Country.objects.get(iso_country_code=visitor_country_code),
                                                exclude=False)
    if len(organizations) == 1:
        slug = organizations[0].slug
        target_url = "/couponfinder/business/" + slug + "/"
        return HttpResponseRedirect(target_url)
    elif len(organizations) <= 0:
        for keyword in search_term_keywords:
            orgs = Organization.objects.filter(name__icontains=keyword,
                                               country=Country.objects.get(iso_country_code=visitor_country_code),
                                               exclude=False)
            organizations = organizations.union(orgs)
    
    #Fix: [#64] Search Autocomplete: Do not list companies, which have no valid offers
    organizations_copy = organizations.all()
    
    for o in organizations_copy:
        if 0 == len(Offer.objects.filter(organization=o, expiry_date__gt=datetime.utcnow())):
            organizations = organizations.filter(~Q(name=o.name))

    context = {'categories': categories, 'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories, 'alert': country_alert,
               'search_term': search_term, 'organizations': organizations, 'current_visitor_country_code': visitor_country_code,
               'active_country': country, 'countries': countries, 'default_country_code': Country.default_country_code}
    template = loader.get_template('couponfinder/results.html')
    r = HttpResponse(template.render(context, request))
    save_signed_cookie(request, r, 'preferences', os.environ['COUPONFINDER_COOKIE_KEY_LOCATION'], visitor_country_code)
    return r


def ajax_search(request):
    search_term = request.GET['term'].strip()
    search_term_keywords = search_term.split(" ")
    visitor_country_code = get_location(request)['visitor_country_code']

    organizations = Organization.objects.filter(name__icontains=search_term,
                                                country=Country.objects.get(iso_country_code=visitor_country_code),
                                                exclude=False)
    if len(organizations) <= 0:
        for keyword in search_term_keywords:
            orgs = Organization.objects.filter(name__icontains=keyword,
                                               country=Country.objects.get(iso_country_code=visitor_country_code),
                                               exclude=False)
            organizations = organizations.union(orgs)
    
    #Fix: [#64] Search Autocomplete: Do not list companies, which have no valid offers
    orgs_with_no_offers = []

    for o in organizations:
        if 0 == len(Offer.objects.filter(organization=o, expiry_date__gt=datetime.utcnow())):
            orgs_with_no_offers.append(o)

    result = diff(list(organizations),orgs_with_no_offers)

    output_dict = {}
    for counter, org in enumerate(result):  
        org_name = org.name
        output_dict[counter] = org_name
 
    return JsonResponse(output_dict)


def ajax_tsandcs(request):
    offer_id = request.GET['terms_id'].strip()
    offer = Offer.objects.get(id=offer_id)
    terms = offer.terms

    if "" == terms:
        terms = "Terms and conditions of " + offer.organization.name + " apply."
    
    return JsonResponse({"terms":terms})

def privacy(request):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    location = get_location(request)
    visitor_country_code = location['visitor_country_code']
    country = location['country']
    countries = Country.objects.filter(iso_country_code__in = Country.target_country_codes)
    country_alert = False
    if Country.default_country_code.lower() == visitor_country_code.lower():
        country_alert = 'Apologies, we do not currently serve your region!'
     
    context = {'categories': categories, 'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories, 
               'alert': country_alert,'current_visitor_country_code': visitor_country_code,'active_country': country, 'countries': countries, 
               'default_country_code': Country.default_country_code}
    template = loader.get_template('couponfinder/privacy.html')
    r = HttpResponse(template.render(context, request))
    save_signed_cookie(request, r, 'preferences', os.environ['COUPONFINDER_COOKIE_KEY_LOCATION'], visitor_country_code)
    return r


def legal(request):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    location = get_location(request)
    visitor_country_code = location['visitor_country_code']
    country = location['country']
    countries = Country.objects.filter(iso_country_code__in = Country.target_country_codes)
    country_alert = False
    if Country.default_country_code.lower() == visitor_country_code.lower():
        country_alert = 'Apologies, we do not currently serve your region!'
     
    context = {'categories': categories, 'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories, 
               'alert': country_alert,'current_visitor_country_code': visitor_country_code,'active_country': country, 'countries': countries, 
               'default_country_code': Country.default_country_code}
    template = loader.get_template('couponfinder/legal.html')
    r = HttpResponse(template.render(context, request))
    save_signed_cookie(request, r, 'preferences', os.environ['COUPONFINDER_COOKIE_KEY_LOCATION'], visitor_country_code)
    return r


#Utility Functions#
def load_file(file_location):
    try:
        with open(file_location, "rb") as f:
            return HttpResponse(f.read(), content_type="image")
    except IOError:
        return HttpResponse('No Image Found!')


