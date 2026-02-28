"""
Analytics URL Configuration
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    
    # Chart API Endpoints
    path('api/charts/disease-accuracy/', views.DiseaseAccuracyChartView.as_view(), name='disease_accuracy_chart'),
    path('api/charts/price-trends/', views.CropPriceTrendsChartView.as_view(), name='price_trends_chart'),
    path('api/charts/prediction-usage/', views.PredictionUsageChartView.as_view(), name='prediction_usage_chart'),
    path('api/charts/farmer-sales/', views.FarmerSalesChartView.as_view(), name='farmer_sales_chart'),
    path('api/charts/soil-statistics/', views.SoilDataStatisticsView.as_view(), name='soil_statistics_chart'),
    path('api/charts/user-growth/', views.UserGrowthChartView.as_view(), name='user_growth_chart'),
    
    # API Endpoints
    path('api/summary/', views.api_analytics_summary, name='api_summary'),
    path('api/model-accuracy/', views.api_model_accuracy, name='api_model_accuracy'),
]
