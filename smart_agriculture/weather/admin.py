"""
Weather Admin Configuration
"""
from django.contrib import admin
from .models import WeatherLog, WeatherAlert, CropWeatherIndex, FarmerWeatherPreference


@admin.register(WeatherLog)
class WeatherLogAdmin(admin.ModelAdmin):
    list_display = ('location', 'date', 'temperature_max', 'temperature_min', 'humidity', 'rainfall', 'weather_condition')
    list_filter = ('weather_condition', 'date')
    search_fields = ('location',)
    date_hierarchy = 'date'


@admin.register(WeatherAlert)
class WeatherAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'alert_type', 'severity', 'start_time', 'is_active')
    list_filter = ('alert_type', 'severity', 'is_active', 'issued_at')
    search_fields = ('title', 'location', 'description')
    date_hierarchy = 'issued_at'


@admin.register(CropWeatherIndex)
class CropWeatherIndexAdmin(admin.ModelAdmin):
    list_display = ('crop', 'location', 'date', 'growing_degree_days', 'irrigation_recommended')
    list_filter = ('irrigation_recommended', 'date')
    search_fields = ('crop', 'location')
    date_hierarchy = 'date'


@admin.register(FarmerWeatherPreference)
class FarmerWeatherPreferenceAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'location', 'daily_forecast', 'weather_alerts', 'updated_at')
    search_fields = ('farmer__name', 'location')
