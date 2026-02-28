"""
Analytics Admin Configuration
"""
from django.contrib import admin
from .models import SystemAnalytics, DailyActivityLog, AIModelPerformance, MarketTrend


@admin.register(SystemAnalytics)
class SystemAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'total_orders', 'total_revenue', 'total_predictions')
    date_hierarchy = 'date'


@admin.register(DailyActivityLog)
class DailyActivityLogAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'user', 'created_at')
    list_filter = ('activity_type', 'created_at')
    search_fields = ('user__name', 'description')
    date_hierarchy = 'created_at'


@admin.register(AIModelPerformance)
class AIModelPerformanceAdmin(admin.ModelAdmin):
    list_display = ('model_type', 'date', 'accuracy', 'total_predictions')
    list_filter = ('model_type', 'date')
    date_hierarchy = 'date'


@admin.register(MarketTrend)
class MarketTrendAdmin(admin.ModelAdmin):
    list_display = ('crop', 'state', 'date', 'avg_price', 'total_volume')
    list_filter = ('date',)
    search_fields = ('crop', 'state', 'market_name')
    date_hierarchy = 'date'
