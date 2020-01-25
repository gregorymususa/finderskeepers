from django.db import models

# Model Field Reference (use in modesls.py):    https://docs.djangoproject.com/en/2.1/ref/models/fields/
# Query Set Reference (use in views.py):        https://docs.djangoproject.com/en/2.1/ref/models/querysets/
# Django Built-ins (use in html templates)      https://docs.djangoproject.com/en/2.1/ref/templates/builtins/

# manage.py makemigrations couponfinder
# manage.py migrate

# manage.py sqlmigrate couponfinder 0001

# Object creation, Date Time Field — YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
# Example: 2018-11-30T23:59:59Z

class Country(models.Model):
    target_country_codes = ('GB','ZZ')
    default_country_code = 'ZZ'
    iso_country_code = models.SlugField('IsoCountryCode', max_length=2, unique=True)
    flag = models.URLField('FlagFilename', max_length=200, blank=True, null=True)
    country = models.CharField("Country", max_length=200, blank=True, null=True)


class Category(models.Model):
    name = models.CharField('Name', max_length=70, unique=True)
    icon = models.URLField('Icon', max_length=200, blank=True)
    slug = models.SlugField('Slug', max_length=70, blank=True, null=True)
    manual_rank = models.SmallIntegerField('ManualRank', unique=True, blank=True, null=True)

    def __str__(self):
        return self.name


class Organization(models.Model):
    """
    An Organization represents the Business which is giving the offer/discount/coupon/sale.

    name        -   [CharField]   Name of Organization
    website     -   [URLField]    URL of the Organization
    logo        -   [URLField]    urls.py URL name; that points to the logo image file
    slug        -   [CharField]   URL slug of the Organization

    """
    AWIN = "AWIN"
    CJ = "CJ"

    sources = (
        (AWIN,"AWIN"),
        (CJ,"CJ"),
    )

    name = models.CharField('Name', max_length=70, default='Missing Organization Name', unique=True)
    slogan = models.TextField('Slogan', blank=True, null=True)
    description = models.TextField('Description', blank=True, null=True)
    website = models.URLField('Website', max_length=200, blank=True)
    affiliate_link = models.URLField('AffiliateLink', max_length=200, blank=True)
    logo = models.URLField('Logo', max_length=200, blank=True)
    external_logo = models.URLField('ExternalLogo', max_length=200, blank=True)
    slug = models.SlugField('Slug', max_length=70, blank=True, null=True)
    program_joined = models.BooleanField('ProgramJoined', default=False)
    exclude = models.BooleanField('Exclude', default=False)
    external_id = models.CharField('ExternalID', max_length=70, unique=True, blank=True, null=True)
    source = models.CharField('Source', max_length=11, choices=sources, blank=True, null=True)
    last_reviewed = models.DateField("LastReviewed", blank=True, null=True)

    country = models.ForeignKey('Country', on_delete=models.CASCADE)
 
    def __str__(self):
        return self.name

    def __lt__(self,other):
        assert isinstance(other,Organization)
        return self.name.lower()<other.name.lower()

    
# TODO documentation strings; including the order of parameters
class Offer(models.Model):
    CODE = "CODE"
    SALE = "SALE"
    AWIN = "AWIN"
    CJ = "CJ"
    labels = (
        (CODE,"Offer Code"),
        (SALE,"Sale"),
    )
    sources = (
        (AWIN,"AWIN"),
        (CJ,"CJ"),
    )
    title = models.TextField('Title', blank=True, null=True)
    description = models.TextField('Description')
    affiliate_link = models.URLField('AffiliateLink', max_length=1000, blank=True, null=True)
    link = models.URLField('Link', max_length=800, blank=True, null=True)
    code = models.CharField('OfferCode', max_length=70, blank=True, null=True)#TODO monitor it's a candidate for UNIQUE (based on in-the-wild behaviour)
    start_date = models.DateTimeField("StartDate", blank=True, null=True)
    expiry_date = models.DateTimeField("ExpiryDate")
    is_while_stocks_last = models.BooleanField("WhileStocksLast", default=False)
    label = models.CharField('Label', max_length=11, choices=labels, blank=True, null=True)
    is_coupon = models.BooleanField("IsCoupon", default=False)
    terms = models.TextField('Terms', blank=True, null=True)
    exclusive = models.BooleanField('Exclusive', default=False)
    exclude = models.BooleanField('Exclude', default=False)
    external_id = models.CharField('ExternalID', max_length=70, unique=True, blank=True, null=True)
    source = models.CharField('Source', max_length=11, choices=sources, blank=True, null=True)
    
    country = models.ForeignKey('Country', on_delete=models.CASCADE) 
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)


