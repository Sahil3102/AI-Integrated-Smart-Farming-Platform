"""
Farmer URL Configuration
"""
from django.urls import path
from . import views

app_name = 'farmer'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.FarmerDashboardView.as_view(), name='dashboard'),
    
    # Crop Management
    path('crops/', views.CropListView.as_view(), name='crop_list'),
    path('crops/add/', views.CropCreateView.as_view(), name='crop_add'),
    path('crops/<int:pk>/edit/', views.CropUpdateView.as_view(), name='crop_edit'),
    path('crops/<int:pk>/delete/', views.CropDeleteView.as_view(), name='crop_delete'),
    
    # Orders
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/update/', views.OrderStatusUpdateView.as_view(), name='order_update'),
    
    # Sales History
    path('sales-history/', views.SalesHistoryView.as_view(), name='sales_history'),
    
    # Prediction History
    path('predictions/', views.PredictionHistoryView.as_view(), name='prediction_history'),
    
    # API Endpoints
    path('api/dashboard-stats/', views.api_farmer_dashboard_stats, name='api_dashboard_stats'),
    path('api/add-crop/', views.api_add_crop, name='api_add_crop'),
    path('api/orders/', views.api_farmer_orders, name='api_orders'),
]
