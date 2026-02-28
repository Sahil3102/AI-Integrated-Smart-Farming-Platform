"""
Weather URL Configuration
"""
from django.urls import path
from django.views.generic import TemplateView

app_name = 'weather'

urlpatterns = [
    # Placeholder views - to be implemented with full CRUD later
    path('', TemplateView.as_view(template_name='home.html'), name='weather_index'),
]
