"""
AI Models URL Configuration
"""
from django.urls import path
from . import views
from . import chatbot_views

app_name = 'ai_models'

urlpatterns = [
    # Web Views
    path('disease-detection/', views.DiseaseDetectionView.as_view(), name='disease_detection'),
    path('price-prediction/', views.PricePredictionView.as_view(), name='price_prediction'),
    path('soil-recommendation/', views.SoilRecommendationView.as_view(), name='soil_recommendation'),
    path('weather-forecast/', views.WeatherForecastView.as_view(), name='weather_forecast'),
    
    # API Endpoints
    path('disease/', views.api_disease_detection, name='api_disease'),
    path('price/', views.api_price_prediction, name='api_price'),
    path('soil/', views.api_soil_recommendation, name='api_soil'),
    path('weather/', views.api_weather_forecast, name='api_weather'),
    path('chat/', chatbot_views.api_chatbot, name='api_chat'),
]
