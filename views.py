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
            if country_code in Country.target_country_codes:
                return country_code
            else:
                return Country.default_country_code
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
        visitor_country_code = request.get_signed_cookie(key=os.environ['COUPONFINDER_COOKIE_KEY_LOCATION'], salt=os.environ['COUPONFINDER_SIGNED_COOKIE_SALT'],
                                                         max_age=31536000)
        country = get_country(visitor_country_code)

        if "POST" == request.method:
            visitor_country_code = request.POST['location-choice']
            country = get_country(visitor_country_code)
    except:
        visitor_country_code = get_visitor_country(request.META['REMOTE_ADDR'])
        country = get_country(visitor_country_code)
    return {'visitor_country_code':visitor_country_code,'country':country}


def save_signed_cookie(request, response, consent_mode, key, value, secure_cookie=True, http_only=True, max_age=31536000):
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

#############################################################################################
# Output Functions                                                                          #
#                                                                                           #
# All "Template Rendering" Views, need to have the following functions called at the start: #
#    categories = get_all_categories()                                                      #
#    footer_categories = get_footer_categories()                                            #
#    addt_footer_categories = get_addt_footer_categories()                                  #
#    visitor_country_code = get_visitor_country(request.META['REMOTE_ADDR'])                #
#    country = get_country(visitor_country_code)                                          #
#                                                                                           #
# Becase base.html uses the data from these results                                         #
#############################################################################################

def index(request):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    visitor_country_code = get_location(request)['visitor_country_code']
    country = get_location(request)['country']
    countries = Country.objects.all()
    
    country_alert = False
    if Country.default_country_code.lower() == visitor_country_code.lower():
        country_alert = 'Apologies, we do not currently serve your region!'

    organizations = Organization.objects.all()
    excluded_orgs = Organization.objects.filter(exclude=True)

    now = datetime.utcnow()

    # TODO select the homepage offers based on impressions / conversion rates

    ##################
    # Small Displays #
    ##################
    sm_fashion = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Fashion"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:4]

    sm_travel = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Travel"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:4]

    sm_experiences = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Experiences"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:4]

    sm_groceries = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Health"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:4]

    sm_restaurants = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Restaurants"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:4]

    sm_sports = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Sports"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:4]

    sm_technology = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Technology"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:4]
    
    sm_offer_range = sm_fashion.union(
        sm_travel, sm_experiences, sm_groceries, sm_restaurants, sm_sports, sm_technology)

    ##################
    # Large Displays #
    ##################
    lg_fashion = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Fashion"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:9]

    lg_travel = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Travel"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:9]

    lg_experiences = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Experiences"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:9]

    lg_groceries = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Health"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:9]

    lg_restaurants = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Restaurants"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:9]

    lg_sports = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Sports"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:9]

    lg_technology = Offer.objects.filter(
        ~Q(organization__in=excluded_orgs),
        category=Category.objects.get(name="Technology"),
        country=Country.objects.get(iso_country_code=visitor_country_code),
        expiry_date__gt=now).order_by('?')[0:9]

    lg_offer_range = lg_fashion.union(
        lg_travel, lg_experiences, lg_groceries, lg_restaurants, lg_sports, lg_technology)

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
    excluded_orgs = Organization.objects.filter(exclude=True)

    visitor_country_code = get_location(request)['visitor_country_code']
    country = get_location(request)['country']
    countries = Country.objects.all()
    country_alert = False
    if Country.default_country_code.lower() == visitor_country_code.lower():
        country_alert = 'Apologies, we do not currently serve your region!'

    now = datetime.utcnow()

    page = request.GET.get("page",False)
    if page != False:
        offers = Paginator(Offer.objects.filter(~Q(organization__in=excluded_orgs),
                                                category=Category.objects.filter(slug=category_name_slug)[0],
                                                country=Country.objects.get(iso_country_code=visitor_country_code),
                                                expiry_date__gt=now),15).page(page)
    else:
        offers = Paginator(Offer.objects.filter(~Q(organization__in=excluded_orgs),
                                                category=Category.objects.filter(slug=category_name_slug)[0],
                                                country=Country.objects.get(iso_country_code=visitor_country_code),
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
 
    excluded_orgs = Organization.objects.filter(exclude=True)

    now = datetime.utcnow()

    visitor_country_code = get_location(request)['visitor_country_code']
    if page != False:
        offers = Paginator(Offer.objects.filter(~Q(organization__in=excluded_orgs),
                                                category=Category.objects.filter(slug=category_name_slug)[0],
                                                country=Country.objects.get(iso_country_code=visitor_country_code),
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
    visitor_country_code = get_location(request)['visitor_country_code']
    country = get_location(request)['country']
    countries = Country.objects.all()
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
    visitor_country_code = get_location(request)['visitor_country_code']
    country = get_location(request)['country']
    countries = Country.objects.all()
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

    output_dict = {}
    for counter,org_name_dict in enumerate(organizations.values('name')):
        org_name = org_name_dict['name']
        output_dict[counter] = org_name
    
    return JsonResponse(output_dict)


def ajax_tsandcs(request):
    offer_id = request.GET['terms_id'].strip()
    offer = Offer.objects.get(id=offer_id)
    terms = offer.terms

    if "" == terms:
        terms = "Terms and Conditions not provided by " + offer.organization.name
    
    return JsonResponse({int(offer_id):terms})


def logo(request):
    try:
        with open(get_file_path("templates/couponfinder/img/white_logo_transparent2.png"), 'rb') as fd:
            return HttpResponse(fd.read(), content_type="image/png")
    except:
        return HttpResponse('No Image Found!')


def travel_icon(request):
    try:
        with open(get_file_path("templates/couponfinder/category_icons/world.png"), "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        return HttpResponse('No Image Found!')


def experiences_icon(request):
    try:
        with open(get_file_path("templates/couponfinder/category_icons/hot-air-balloon.png"), "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        return HttpResponse('No Image Found!')


def fashion_icon(request):
    try:
        with open(get_file_path("templates/couponfinder/category_icons/fashion.png"), "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        return HttpResponse('No Image Found!')


def bootstrap_css(request):
    try:
        with open(get_file_path("templates/couponfinder/css/bootstrap.css"), "rt") as f:
            return HttpResponse(f.read(), content_type="text/css")
    except IOError:
        return HttpResponse('bootstrap.css not found!')


def couponfinder_css(request):
    try:
        with open(get_file_path("templates/couponfinder/css/couponfinder.css"), "rt") as f:
            return HttpResponse(f.read(), content_type="text/css")
    except IOError:
        return HttpResponse('couponfinder.css not found!')


# Organization Logos #
# TODO change all file loading functions, to use an overloaded load_file function #
# TODO During go-live: change the file paths, in this file — to point to the files, on the server #

def load_file(file_location):
    try:
        with open(file_location, "rb") as f:
            return HttpResponse(f.read(), content_type="image")
    except IOError:
        return HttpResponse('No Image Found!')


def couponfinder_org_Thomas_Cook(request):
    return load_file(
        'F:\LearnPython\mysite3\couponfinder\\templates\couponfinder\organization_logos\Thomas_Cook.png')
