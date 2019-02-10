from django.db import models

# Model Field Reference (use in modesls.py):    https://docs.djangoproject.com/en/2.1/ref/models/fields/
# Query Set Reference (use in views.py):        https://docs.djangoproject.com/en/2.1/ref/models/querysets/
# Django Built-ins (use in html templates)      https://docs.djangoproject.com/en/2.1/ref/templates/builtins/

# manage.py makemigrations couponfinder
# manage.py migrate

# manage.py sqlmigrate couponfinder 0001

# Object creation, Date Time Field — YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
# Example: 2018-11-30T23:59:59Z

class Category(models.Model):
    name = models.CharField('Name', max_length=70, primary_key=True)
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
    category    -   [ForeignKey]  category=Category.objects.get(<attribute>='<value>')

    """
    name = models.CharField('Name', max_length=70, primary_key=True)
    website = models.URLField('Website', max_length=200, blank=True)
    logo = models.URLField('Logo', max_length=200, blank=True)
    slug = models.SlugField('Slug', max_length=70, blank=True, null=True)
    category = models.ManyToManyField(Category)

    def __str__(self):
        return self.name

    
# TODO documentation strings; including the order of parameters
class Offer(models.Model):
    CODE = "CODE"
    SALE = "SALE"
    labels = (
        (CODE,"Offer Code"),
        (SALE,"Sale"),
    )
    description = models.TextField('Description')
    affiliate_link = models.URLField('AffiliateLink', max_length=200, blank=True, null=True)
    code = models.CharField('OfferCode', max_length=70, blank=True, null=True)#TODO monitor it's a candidate for UNIQUE (based on in-the-wild behaviour)
    expiry_date = models.DateTimeField("ExpiryDate")
    is_while_stocks_last = models.BooleanField("WhileStocksLast", default=False)
    label = models.CharField('Label', max_length=11, choices=labels, blank=True, null=True)
    terms = models.TextField('Terms', blank=True, null=True)
    external_id = models.CharField('ExternalID', max_length=70, unique=True, blank=True, null=True)
    
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    organization = models.ForeignKey('Organization', on_delete=models.CASCADE)