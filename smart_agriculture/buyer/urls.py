"""
Buyer URL Configuration
"""
from django.urls import path
from . import views

app_name = 'buyer'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.BuyerDashboardView.as_view(), name='dashboard'),
    
    # Browse Crops
    path('browse/', views.BrowseCropsView.as_view(), name='browse_crops'),
    path('crop/<int:pk>/', views.CropDetailView.as_view(), name='crop_detail'),
    path('crop/<int:pk>/buy/', views.BuyCropView.as_view(), name='buy_crop'),
    
    # Orders
    path('orders/', views.OrderHistoryView.as_view(), name='order_history'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    
    # Farmer Profile
    path('farmer/<int:farmer_id>/', views.FarmerProfileView.as_view(), name='farmer_profile'),
    
    # Wishlist
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/<int:crop_id>/', views.AddToWishlistView.as_view(), name='add_wishlist'),
    path('wishlist/remove/<int:crop_id>/', views.RemoveFromWishlistView.as_view(), name='remove_wishlist'),
    
    # API Endpoints
    path('api/dashboard-stats/', views.api_buyer_dashboard_stats, name='api_dashboard_stats'),
    path('api/browse/', views.api_browse_crops, name='api_browse_crops'),
    path('api/buy/', views.api_buy_crop, name='api_buy_crop'),
]
