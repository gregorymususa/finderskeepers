from django.urls import path
from . import views

# TODO app_name (https://docs.djangoproject.com/en/2.1/intro/tutorial03/)
urlpatterns = [
    path('', views.index, name='index'),
    path('business/<slug:business_name_slug>/', views.business, name="business"),
    path('category/<slug:category_name_slug>/', views.category, name="category"),
    path('privacy/', views.privacy, name="privacy"),
    path('terms/', views.terms, name="terms"),
    path('legal/', views.legal, name="legal"),
    path('results/', views.search, name="results"),
    path('ajax_search/', views.ajax_search, name="ajax_search"),
    path('ajax_category/<slug:category_name_slug>/', views.ajax_category, name="ajax_category"),
    path('ajax_tsandcs/', views.ajax_tsandcs, name="ajax_tsandcs"),
]
