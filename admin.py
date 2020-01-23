from django.contrib import admin
from .models import Country, Category, Organization, Offer
# Register your models here.

admin.site.register(Country)
admin.site.register(Category)
admin.site.register(Organization)
admin.site.register(Offer)


