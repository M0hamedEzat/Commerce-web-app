from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name='create'),
    path("listing/<int:listing_id>", views.listing_details, name='listing_details'),
    path('watchlist/<int:item_id>', views.watchlist, name='watch'),
    path('close/<int:item_id>', views.close, name='close'),
    path('mywatchlist', views.mywatchlist, name='mywatchlist'),
]
