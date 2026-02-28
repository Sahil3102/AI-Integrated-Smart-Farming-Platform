"""
Buyer Admin Configuration
"""
from django.contrib import admin
from .models import BuyerPreferences, BuyerAnalytics, CropSearchHistory, Wishlist


@admin.register(BuyerPreferences)
class BuyerPreferencesAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'prefer_organic', 'notifications_enabled', 'updated_at')
    search_fields = ('buyer__name', 'buyer__email')


@admin.register(BuyerAnalytics)
class BuyerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'total_orders', 'total_spent', 'last_updated')
    search_fields = ('buyer__name', 'buyer__email')


@admin.register(CropSearchHistory)
class CropSearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'search_query', 'results_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('buyer__name', 'search_query')
    date_hierarchy = 'created_at'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'crop', 'added_at')
    search_fields = ('buyer__name', 'crop__name')
