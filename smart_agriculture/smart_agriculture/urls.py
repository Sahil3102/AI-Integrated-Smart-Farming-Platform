"""
URL configuration for smart_agriculture project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('accounts/', include('smart_agriculture.accounts.urls')),
    path('farmer/', include('smart_agriculture.farmer.urls')),
    path('buyer/', include('smart_agriculture.buyer.urls')),
    path('analytics/', include('smart_agriculture.analytics.urls')),
    path('api/', include('smart_agriculture.ai_models.urls')),
    path('soil/', include('smart_agriculture.soil.urls')),
    path('weather/', include('smart_agriculture.weather.urls')),
    path('dashboard/', include('smart_agriculture.core_dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
