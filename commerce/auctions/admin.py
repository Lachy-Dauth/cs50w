from django.contrib import admin
from .models import *

class WatchingAdmin(admin.ModelAdmin):
    filter_horizontal = ("watching",)

admin.site.register(User, WatchingAdmin)
admin.site.register(Category)
admin.site.register(Auction)
admin.site.register(Bid)
admin.site.register(Comment)
