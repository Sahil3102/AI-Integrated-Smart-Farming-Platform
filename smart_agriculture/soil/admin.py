"""
Soil Admin Configuration
"""
from django.contrib import admin
from .models import SoilData, SoilTestReport, FertilizerApplication


@admin.register(SoilData)
class SoilDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'test_date', 'ph_level', 'npk_ratio', 'created_at')
    list_filter = ('test_date', 'soil_texture', 'created_at')
    search_fields = ('user__name', 'location')
    date_hierarchy = 'test_date'


@admin.register(SoilTestReport)
class SoilTestReportAdmin(admin.ModelAdmin):
    list_display = ('soil_data', 'fertility_rating', 'created_at')
    list_filter = ('fertility_rating',)


@admin.register(FertilizerApplication)
class FertilizerApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'fertilizer_name', 'crop', 'application_date', 'quantity_applied')
    list_filter = ('fertilizer_type', 'application_method', 'application_date')
    search_fields = ('user__name', 'fertilizer_name', 'crop')
    date_hierarchy = 'application_date'
