from django.contrib import admin
from .models import User, AuctionListing, Bid, Comment
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_superuser","password")

class ListingAdmin(admin.ModelAdmin):
    list_display = ("title", "starting_bid","current_price", "created_at", "updated_at", "owner", "is_active")

admin.site.register(User, UserAdmin)
admin.site.register(AuctionListing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Comment)

