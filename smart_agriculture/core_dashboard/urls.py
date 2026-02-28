"""
Core Dashboard URL Configuration
"""
from django.urls import path
from . import views

app_name = 'core_dashboard'

urlpatterns = [
    # Main Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Admin Dashboard
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/users/', views.AdminUserManagementView.as_view(), name='admin_user_management'),
    path('admin/users/<int:user_id>/toggle/', views.AdminToggleUserStatusView.as_view(), name='admin_toggle_user'),
    path('admin/logs/', views.SystemLogsView.as_view(), name='system_logs'),
]
