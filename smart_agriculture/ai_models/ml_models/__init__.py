"""
AI/ML Models Package
"""
from .disease_detection import detect_disease, DiseaseDetectionModel
from .price_prediction import predict_price, PricePredictionModel
from .soil_recommendation import recommend_crop, SoilRecommendationModel
from .weather_forecast import get_weather_forecast, get_current_weather, WeatherForecastModel

__all__ = [
    'detect_disease',
    'DiseaseDetectionModel',
    'predict_price',
    'PricePredictionModel',
    'recommend_crop',
    'SoilRecommendationModel',
    'get_weather_forecast',
    'get_current_weather',
    'WeatherForecastModel',
]
