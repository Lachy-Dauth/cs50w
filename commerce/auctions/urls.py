from django.urls import path
from . import views

# app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new-listing", views.new_listing_view, name="new_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("category/<int:category_id>", views.category, name="category"),
    path("category", views.category_finder, name="category_finder"),
]
