from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.template import Template, context, loader
from .models import Category, Organization, Offer, Flag
from django.core.paginator import Paginator
import json, os, requests

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
            return output_json['countryCode']
        else:
            return "False"
    except:
        return "trace" 


def get_country_flag(iso_country_code):
    """
    Returns Flag object (from Models.py), corresponding to the supplied two-digi iso_country_code
    ---------------------------------------------------------------------------------------------
    iso_country_code : str (two-digit iso code)
    """
    try:
        f = Flag.objects.get(iso_country_code=iso_country_code)
    except:
        return Flag.objects.get(iso_country_code='ZZ')
    return f


#############################################################################################
# Output Functions                                                                          #
#                                                                                           #
# All "Template Rendering" Views, need to have the following functions called at the start: #
#    categories = get_all_categories()                                                      #
#    footer_categories = get_footer_categories()                                            #
#    addt_footer_categories = get_addt_footer_categories()                                  #
#    visitor_country_code = get_visitor_country(request.META['REMOTE_ADDR'])                #
#    flag = get_country_flag(visitor_country_code)                                          #
#                                                                                           #
# Becase base.html uses the data from these results                                         #
#############################################################################################

def index(request):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    visitor_country_code = get_visitor_country(request.META['REMOTE_ADDR'])
    flag = get_country_flag(visitor_country_code)
    flags = Flag.objects.all()
    
    organizations = Organization.objects.all()
    offers = Offer.objects.all()

    # TODO select the homepage offers based on impressions / conversion rates

    ##################
    # Small Displays #
    ##################
    sm_fashion = Offer.objects.filter(
        category=Category.objects.get(name="Fashion")).order_by('?')[0:4]

    sm_travel = Offer.objects.filter(
        category=Category.objects.get(name="Travel")).order_by('?')[0:4]

    sm_experiences = Offer.objects.filter(
        category=Category.objects.get(name="Experiences")).order_by('?')[0:4]

    sm_groceries = Offer.objects.filter(
        category=Category.objects.get(name="Health")).order_by('?')[0:4]

    sm_restaurants = Offer.objects.filter(
        category=Category.objects.get(name="Restaurants")).order_by('?')[0:4]

    sm_sports = Offer.objects.filter(
        category=Category.objects.get(name="Sports")).order_by('?')[0:4]

    sm_technology = Offer.objects.filter(
        category=Category.objects.get(name="Technology")).order_by('?')[0:4]
    
    sm_offer_range = sm_fashion.union(
        sm_travel, sm_experiences, sm_groceries, sm_restaurants, sm_sports, sm_technology)

    ##################
    # Large Displays #
    ##################
    lg_fashion = Offer.objects.filter(
        category=Category.objects.get(name="Fashion")).order_by('?')[0:9]

    lg_travel = Offer.objects.filter(
        category=Category.objects.get(name="Travel")).order_by('?')[0:9]

    lg_experiences = Offer.objects.filter(
        category=Category.objects.get(name="Experiences")).order_by('?')[0:9]

    lg_groceries = Offer.objects.filter(
        category=Category.objects.get(name="Health")).order_by('?')[0:9]

    lg_restaurants = Offer.objects.filter(
        category=Category.objects.get(name="Restaurants")).order_by('?')[0:9]

    lg_sports = Offer.objects.filter(
        category=Category.objects.get(name="Sports")).order_by('?')[0:9]

    lg_technology = Offer.objects.filter(
        category=Category.objects.get(name="Technology")).order_by('?')[0:9]

    lg_offer_range = lg_fashion.union(
        lg_travel, lg_experiences, lg_groceries, lg_restaurants, lg_sports, lg_technology)

    context = {'categories': categories, 'organizations': organizations, 'offers': offers,
               'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories,
               'sm_offer_range': sm_offer_range, 'lg_offer_range': lg_offer_range, 'visitor_country_code': visitor_country_code, 'flag': flag, 'flags': flags}
    template = loader.get_template('couponfinder/index.html')
    return HttpResponse(template.render(context, request))


def category(request, category_name_slug):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    visitor_country_code = get_visitor_country(request.META['REMOTE_ADDR'])
    flag = get_country_flag(visitor_country_code)
    flags = Flag.objects.all()

    page = request.GET.get("page",False)
    if page != False:
        offers = Paginator(Offer.objects.filter(category=Category.objects.filter(slug=category_name_slug)[0]),15).page(page)
    else:
        offers = Paginator(Offer.objects.filter(category=Category.objects.filter(slug=category_name_slug)[0]),15).page(1)

    category = Category.objects.filter(slug=category_name_slug)[0]

    context = {'categories': categories, 'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories,
               'offers': offers, 'category': category, 'visitor_country_code': visitor_country_code, 'flag': flag, 'flags': flags}
    template = loader.get_template('couponfinder/category.html')
    return HttpResponse(template.render(context, request))


def ajax_category(request, category_name_slug):
    page = request.GET.get("page",False)
    media = request.GET.get("media", False)
    if page != False:
        offers = Paginator(Offer.objects.filter(category=Category.objects.filter(slug=category_name_slug)[0]),15).page(page)

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
    visitor_country_code = get_visitor_country(request.META['REMOTE_ADDR'])
    flag = get_country_flag(visitor_country_code)
    flags = Flag.objects.all()

    offers = Offer.objects.filter(organization=Organization.objects.get(slug=business_name_slug))
    
    organization = Organization.objects.get(slug=business_name_slug)

    context = {'categories': categories, 'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories,
               'business_name_slug': business_name_slug, 'organization': organization, 'offers': offers, 'visitor_country_code': visitor_country_code, 'flag': flag, 'flags': flags}
    template = loader.get_template('couponfinder/business.html')
    return HttpResponse(template.render(context, request))


def search(request):
    categories = get_all_categories()
    footer_categories = get_footer_categories()
    addt_footer_categories = get_addt_footer_categories()
    visitor_country_code = get_visitor_country(request.META['REMOTE_ADDR'])
    flag = get_country_flag(visitor_country_code)
    flags = Flag.objects.all()

    search_term = request.GET['business_name'].strip()
    search_term_keywords = search_term.split(" ")

    organizations = Organization.objects.filter(name__icontains=search_term)
    if len(organizations) == 1:
        slug = organizations[0].slug
        target_url = "/couponfinder/business/" + slug + "/"
        return HttpResponseRedirect(target_url)
    elif len(organizations) <= 0:
        for keyword in search_term_keywords:
            orgs = Organization.objects.filter(name__icontains=keyword)
            organizations = organizations.union(orgs)

    context = {'categories': categories, 'footer_categories': footer_categories, 'addt_footer_categories': addt_footer_categories,
               'search_term': search_term, 'organizations': organizations, 'visitor_country_code': visitor_country_code, 'flag': flag, 'flags': flags}
    template = loader.get_template('couponfinder/results.html')
    return HttpResponse(template.render(context, request))


def ajax_search(request):
    search_term = request.GET['term'].strip()
    search_term_keywords = search_term.split(" ")

    organizations = Organization.objects.filter(name__icontains=search_term)
    if len(organizations) <= 0:
        for keyword in search_term_keywords:
            orgs = Organization.objects.filter(name__icontains=keyword)
            organizations = organizations.union(orgs)

    output_dict = {}
    for counter,org_name_dict in enumerate(organizations.values('name')):
        org_name = org_name_dict['name']
        output_dict[counter] = org_name
    
    return JsonResponse(output_dict)


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
