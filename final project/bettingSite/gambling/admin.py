from django.contrib import admin
from .models import *

# Register the custom User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'balance', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

# Register the Bet model
@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'reserve', 'created_at', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active', 'created_at')

# Register the BetOption model
@admin.register(BetOption)
class BetOptionAdmin(admin.ModelAdmin):
    list_display = ('bet', 'name', 'tickets_sold')
    search_fields = ('name', 'bet__name')
    list_filter = ('bet',)

# Register the Ticket model
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('user', 'option', 'price', 'purchased_at')
    search_fields = ('user__username', 'option__name', 'option__bet__name')
    list_filter = ('option__bet', 'purchased_at')

admin.site.register(ProfitRecord)
admin.site.register(UserStat)