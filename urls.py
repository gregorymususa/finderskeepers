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
    path('fashion-icon/', views.fashion_icon, name='/fashion-icon'),
    path('bootstrap-css/', views.bootstrap_css, name="bootstrap-css"),
    path('couponfinder-css/', views.couponfinder_css, name="couponfinder-css"),
    path('couponfinder_org_365_Tickets/', views.couponfinder_org_365_Tickets,
         name="couponfinder_org_365_Tickets"),
    path('couponfinder_org_999Inks/', views.couponfinder_org_999Inks,
         name="couponfinder_org_999Inks"),
    path('couponfinder_org_Abel_Cole/', views.couponfinder_org_Abel_Cole,
         name="couponfinder_org_Abel_Cole"),
    path('couponfinder_org_Activity_Superstore/', views.couponfinder_org_Activity_Superstore,
         name="couponfinder_org_Activity_Superstore"),
    path('couponfinder_org_adidas/', views.couponfinder_org_adidas,
         name="couponfinder_org_adidas"),
    path('couponfinder_org_All_Bar_One/', views.couponfinder_org_All_Bar_One,
         name="couponfinder_org_All_Bar_One"),
    path('couponfinder_org_ao/', views.couponfinder_org_ao,
         name="couponfinder_org_ao"),
    path('couponfinder_org_Asda/', views.couponfinder_org_Asda,
         name="couponfinder_org_Asda"),
    path('couponfinder_org_ATG_Tickets/', views.couponfinder_org_ATG_Tickets,
         name="couponfinder_org_ATG_Tickets"),
    path('couponfinder_org_Attraction_Tickets_Direct/', views.couponfinder_org_Attraction_Tickets_Direct,
         name="couponfinder_org_Attraction_Tickets_Direct"),
    path('couponfinder_org_AX_Hotels/', views.couponfinder_org_AX_Hotels,
         name="couponfinder_org_AX_Hotels"),
    path('couponfinder_org_Bakerdays/', views.couponfinder_org_Bakerdays,
         name="couponfinder_org_Bakerdays"),
    path('couponfinder_org_Banggood_com/', views.couponfinder_org_Banggood_com,
         name="couponfinder_org_Banggood_com"),
    path('couponfinder_org_Beer_Hawk/', views.couponfinder_org_Beer_Hawk,
         name="couponfinder_org_Beer_Hawk"),
    path('couponfinder_org_Belgo/', views.couponfinder_org_Belgo,
         name="couponfinder_org_Belgo"),
    path('couponfinder_org_Bella_Italia/', views.couponfinder_org_Bella_Italia,
         name="couponfinder_org_Bella_Italia"),
    path('couponfinder_org_Biscuiteers/', views.couponfinder_org_Biscuiteers,
         name="couponfinder_org_Biscuiteers"),
    path('couponfinder_org_Boden/', views.couponfinder_org_Boden,
         name="couponfinder_org_Boden"),
    path('couponfinder_org_Browns_Restaurant/', views.couponfinder_org_Browns_Restaurant,
         name="couponfinder_org_Browns_Restaurant"),
    path('couponfinder_org_Carluccios/', views.couponfinder_org_Carluccios,
         name="couponfinder_org_Carluccios"),
    path('couponfinder_org_Cartridge_People/', views.couponfinder_org_Cartridge_People,
         name="couponfinder_org_Cartridge_People"),
    path('couponfinder_org_Charles_Tyrwhitt_Shirts/', views.couponfinder_org_Charles_Tyrwhitt_Shirts,
         name="couponfinder_org_Charles_Tyrwhitt_Shirts"),
    path('couponfinder_org_Cheltenham_Racecourse/', views.couponfinder_org_Cheltenham_Racecourse,
         name="couponfinder_org_Cheltenham_Racecourse"),
    path('couponfinder_org_Chi_Chi/', views.couponfinder_org_Chi_Chi,
         name="couponfinder_org_Chi_Chi"),
    path('couponfinder_org_Chicken_Cottage/', views.couponfinder_org_Chicken_Cottage,
         name="couponfinder_org_Chicken_Cottage"),
    path('couponfinder_org_Debenhams/', views.couponfinder_org_Debenhams,
         name="couponfinder_org_Debenhams"),
    path('couponfinder_org_Deliveroo/', views.couponfinder_org_Deliveroo,
         name="couponfinder_org_Deliveroo"),
    path('couponfinder_org_GoCompare/', views.couponfinder_org_GoCompare,
         name="couponfinder_org_GoCompare"),
    path('couponfinder_org_I_Saw_It_First/', views.couponfinder_org_I_Saw_It_First,
         name="couponfinder_org_I_Saw_It_First"),
    path('couponfinder_org_Iberostar/', views.couponfinder_org_Iberostar,
         name="couponfinder_org_Iberostar"),
    path('couponfinder_org_La_Redoute/', views.couponfinder_org_La_Redoute,
         name="couponfinder_org_La_Redoute"),
    path('couponfinder_org_Senior_Railcard/', views.couponfinder_org_Senior_Railcard,
         name="couponfinder_org_Senior_Railcard"),
    path('couponfinder_org_Tesco/', views.couponfinder_org_Tesco,
         name="couponfinder_org_Tesco"),
    path('couponfinder_org_The_London_Dungeon/', views.couponfinder_org_The_London_Dungeon,
         name="couponfinder_org_The_London_Dungeon"),
    path('couponfinder_org_Thomas_Cook/', views.couponfinder_org_Thomas_Cook,
         name="couponfinder_org_Thomas_Cook"),
]
