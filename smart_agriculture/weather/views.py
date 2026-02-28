"""
Weather Views
"""
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView

from .models import WeatherLog, WeatherAlert, FarmerWeatherPreference


class WeatherLogListView(LoginRequiredMixin, ListView):
    """List weather logs"""
    model = WeatherLog
    template_name = 'weather/weather_logs.html'
    context_object_name = 'weather_logs'
    paginate_by = 30


class WeatherAlertListView(LoginRequiredMixin, ListView):
    """List weather alerts"""
    model = WeatherAlert
    template_name = 'weather/weather_alerts.html'
    context_object_name = 'alerts'
    
    def get_queryset(self):
        return WeatherAlert.objects.filter(is_active=True)
