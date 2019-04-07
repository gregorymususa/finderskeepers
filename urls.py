from django.urls import path
from . import views

# TODO app_name (https://docs.djangoproject.com/en/2.1/intro/tutorial03/)
urlpatterns = [
    path('', views.index, name='index'),
    path('business/<slug:business_name_slug>/', views.business, name="business"),
    path('category/<slug:category_name_slug>/', views.category, name="category"),
    path('results/', views.search, name="results"),
    path('ajax_search/', views.ajax_search, name="ajax_search"),
    path('ajax_category/<slug:category_name_slug>/', views.ajax_category, name="ajax_category"),
    path('logo/', views.logo, name='logo'),
    path('travel-icon/', views.travel_icon, name='travel-icon'),
    path('experiences-icon/', views.experiences_icon, name='experiences-icon'),
    path('fashion-icon/', views.fashion_icon, name='fashion-icon'),
    path('bootstrap-css/', views.bootstrap_css, name="bootstrap-css"),
    path('couponfinder-css/', views.couponfinder_css, name="couponfinder-css"),
]
