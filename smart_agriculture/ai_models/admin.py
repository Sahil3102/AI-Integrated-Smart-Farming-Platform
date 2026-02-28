"""
AI Models Admin Configuration
"""
from django.contrib import admin
from .models import (
    DiseaseDetectionResult, CropPricePrediction, 
    SoilRecommendation, WeatherForecast,
    AIModelMetrics, ModelTrainingLog
)


@admin.register(DiseaseDetectionResult)
class DiseaseDetectionResultAdmin(admin.ModelAdmin):
    list_display = ('disease_name', 'user', 'confidence_score', 'severity_level', 'created_at')
    list_filter = ('severity_level', 'disease_name', 'created_at')
    search_fields = ('disease_name', 'user__name', 'user__email')
    date_hierarchy = 'created_at'


@admin.register(CropPricePrediction)
class CropPricePredictionAdmin(admin.ModelAdmin):
    list_display = ('crop_name', 'state', 'predicted_price', 'price_trend', 'created_at')
    list_filter = ('price_trend', 'season', 'created_at')
    search_fields = ('crop_name', 'state')
    date_hierarchy = 'created_at'


@admin.register(SoilRecommendation)
class SoilRecommendationAdmin(admin.ModelAdmin):
    list_display = ('recommended_crop', 'user', 'confidence_score', 'ph_level', 'created_at')
    list_filter = ('recommended_crop', 'created_at')
    search_fields = ('recommended_crop', 'user__name')
    date_hierarchy = 'created_at'


@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ('location', 'forecast_date', 'temperature_max', 'temperature_min', 'weather_condition')
    list_filter = ('weather_condition', 'forecast_date')
    search_fields = ('location',)
    date_hierarchy = 'forecast_date'


@admin.register(AIModelMetrics)
class AIModelMetricsAdmin(admin.ModelAdmin):
    list_display = ('model_type', 'model_version', 'accuracy', 'total_predictions', 'last_updated')
    list_filter = ('model_type', 'last_updated')
    search_fields = ('model_version',)


@admin.register(ModelTrainingLog)
class ModelTrainingLogAdmin(admin.ModelAdmin):
    list_display = ('model_type', 'status', 'dataset_size', 'final_accuracy', 'created_at')
    list_filter = ('model_type', 'status', 'created_at')
    date_hierarchy = 'created_at'
