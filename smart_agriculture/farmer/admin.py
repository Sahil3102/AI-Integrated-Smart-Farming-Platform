"""
Farmer Admin Configuration
"""
from django.contrib import admin
from .models import FarmerCrop, Order, SalesHistory, FarmerAnalytics, PredictionHistory


@admin.register(FarmerCrop)
class FarmerCropAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'price_per_kg', 'quantity_kg', 'status', 'created_at')
    list_filter = ('status', 'is_organic', 'created_at')
    search_fields = ('name', 'variety', 'farmer__name', 'farmer__email')
    date_hierarchy = 'created_at'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'buyer', 'farmer', 'crop', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'delivered_on_time')
    search_fields = ('order_id', 'buyer__name', 'farmer__name', 'crop__name')
    date_hierarchy = 'created_at'


@admin.register(SalesHistory)
class SalesHistoryAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'crop_name', 'quantity_sold', 'amount_received', 'sale_date')
    list_filter = ('sale_date',)
    search_fields = ('farmer__name', 'crop_name', 'buyer_name')
    date_hierarchy = 'sale_date'


@admin.register(FarmerAnalytics)
class FarmerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'total_sales', 'total_revenue', 'average_rating', 'last_updated')
    search_fields = ('farmer__name', 'farmer__email')


@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'prediction_type', 'confidence_score', 'created_at')
    list_filter = ('prediction_type', 'created_at')
    search_fields = ('farmer__name', 'farmer__email')
    date_hierarchy = 'created_at'
