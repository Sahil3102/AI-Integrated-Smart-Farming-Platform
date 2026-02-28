"""
Soil Views
"""
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import SoilData, SoilTestReport, FertilizerApplication


class SoilDataListView(LoginRequiredMixin, ListView):
    """List all soil test data for the user"""
    model = SoilData
    template_name = 'soil/soil_data_list.html'
    context_object_name = 'soil_data_list'
    
    def get_queryset(self):
        return SoilData.objects.filter(user=self.request.user)


class FertilizerApplicationListView(LoginRequiredMixin, ListView):
    """List all fertilizer applications for the user"""
    model = FertilizerApplication
    template_name = 'soil/fertilizer_list.html'
    context_object_name = 'fertilizer_applications'
    
    def get_queryset(self):
        return FertilizerApplication.objects.filter(user=self.request.user)
