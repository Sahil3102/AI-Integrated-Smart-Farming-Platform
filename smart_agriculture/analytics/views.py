"""
Analytics Views - Dashboard with Chart.js integration
"""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from smart_agriculture.accounts.models import User
from smart_agriculture.farmer.models import FarmerCrop, Order, PredictionHistory
from smart_agriculture.ai_models.models import (
    DiseaseDetectionResult, CropPricePrediction, 
    SoilRecommendation, AIModelMetrics
)
from .models import SystemAnalytics, AIModelPerformance, DailyActivityLog


class AnalystRequiredMixin(UserPassesTestMixin):
    """Mixin to check if user is an analyst or admin"""
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.role in ['analyst', 'admin']


class AnalyticsDashboardView(LoginRequiredMixin, AnalystRequiredMixin, TemplateView):
    """
    Analytics Dashboard View with Chart.js charts
    """
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # User statistics
        context['total_users'] = User.objects.count()
        context['farmers_count'] = User.objects.filter(role='farmer').count()
        context['buyers_count'] = User.objects.filter(role='buyer').count()
        context['admins_count'] = User.objects.filter(role='admin').count()
        context['analysts_count'] = User.objects.filter(role='analyst').count()
        
        # Crop statistics
        context['total_crops'] = FarmerCrop.objects.count()
        context['available_crops'] = FarmerCrop.objects.filter(status='available').count()
        context['sold_crops'] = FarmerCrop.objects.filter(status='sold').count()
        
        # Order statistics
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(status='pending').count()
        context['completed_orders'] = Order.objects.filter(status='completed').count()
        context['total_revenue'] = Order.objects.filter(
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Prediction statistics
        context['total_predictions'] = PredictionHistory.objects.count()
        context['disease_predictions'] = PredictionHistory.objects.filter(
            prediction_type='disease'
        ).count()
        context['price_predictions'] = PredictionHistory.objects.filter(
            prediction_type='price'
        ).count()
        context['soil_predictions'] = PredictionHistory.objects.filter(
            prediction_type='soil'
        ).count()
        
        # AI Model accuracy
        context['model_metrics'] = AIModelMetrics.objects.all()
        
        # Recent activity
        context['recent_activity'] = DailyActivityLog.objects.select_related('user')[:20]
        
        return context


class DiseaseAccuracyChartView(LoginRequiredMixin, AnalystRequiredMixin, View):
    """
    API endpoint for disease detection accuracy chart data
    """
    def get(self, request):
        # Get last 30 days of disease detection results
        from django.utils import timezone
        from datetime import timedelta
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        results = DiseaseDetectionResult.objects.filter(
            created_at__range=(start_date, end_date)
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id'),
            avg_confidence=Avg('confidence_score')
        ).order_by('date')
        
        labels = [r['date'].strftime('%Y-%m-%d') for r in results]
        counts = [r['count'] for r in results]
        confidences = [round(r['avg_confidence'], 2) for r in results]
        
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Detections',
                    'data': counts,
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                    'yAxisID': 'y',
                },
                {
                    'label': 'Avg Confidence (%)',
                    'data': confidences,
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'yAxisID': 'y1',
                }
            ]
        })


class CropPriceTrendsChartView(LoginRequiredMixin, AnalystRequiredMixin, View):
    """
    API endpoint for crop price trends chart data
    """
    def get(self, request):
        crop = request.GET.get('crop', 'wheat')
        
        predictions = CropPricePrediction.objects.filter(
            crop_name__iexact=crop
        ).order_by('created_at')[:30]
        
        labels = [p.created_at.strftime('%Y-%m-%d') for p in predictions]
        prices = [float(p.predicted_price) for p in predictions]
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'label': f'{crop.title()} Price (Rs/kg)',
                'data': prices,
                'borderColor': 'rgb(54, 162, 235)',
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'fill': True,
                'tension': 0.4
            }]
        })


class PredictionUsageChartView(LoginRequiredMixin, AnalystRequiredMixin, View):
    """
    API endpoint for prediction usage chart data
    """
    def get(self, request):
        # Get prediction counts by type
        predictions = PredictionHistory.objects.values(
            'prediction_type'
        ).annotate(
            count=Count('id')
        )
        
        labels = []
        data = []
        colors = [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
        ]
        
        type_names = {
            'disease': 'Disease Detection',
            'price': 'Price Prediction',
            'soil': 'Soil Recommendation',
            'weather': 'Weather Forecast',
        }
        
        for i, p in enumerate(predictions):
            labels.append(type_names.get(p['prediction_type'], p['prediction_type']))
            data.append(p['count'])
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors[:len(data)],
                'borderWidth': 1
            }]
        })


class FarmerSalesChartView(LoginRequiredMixin, AnalystRequiredMixin, View):
    """
    API endpoint for farmer sales chart data
    """
    def get(self, request):
        # Get top 10 farmers by sales
        from smart_agriculture.farmer.models import SalesHistory
        
        top_farmers = SalesHistory.objects.values(
            'farmer__name'
        ).annotate(
            total_sales=Sum('amount_received'),
            order_count=Count('id')
        ).order_by('-total_sales')[:10]
        
        labels = [f['farmer__name'] for f in top_farmers]
        sales = [float(f['total_sales']) for f in top_farmers]
        orders = [f['order_count'] for f in top_farmers]
        
        return JsonResponse({
            'labels': labels,
            'datasets': [
                {
                    'label': 'Total Sales (Rs)',
                    'data': sales,
                    'backgroundColor': 'rgba(75, 192, 192, 0.8)',
                    'yAxisID': 'y',
                },
                {
                    'label': 'Order Count',
                    'data': orders,
                    'backgroundColor': 'rgba(255, 159, 64, 0.8)',
                    'yAxisID': 'y1',
                }
            ]
        })


class SoilDataStatisticsView(LoginRequiredMixin, AnalystRequiredMixin, View):
    """
    API endpoint for soil data statistics
    """
    def get(self, request):
        from smart_agriculture.soil.models import SoilData
        
        # Get average NPK values
        avg_n = SoilData.objects.aggregate(avg=Avg('nitrogen'))['avg'] or 0
        avg_p = SoilData.objects.aggregate(avg=Avg('phosphorus'))['avg'] or 0
        avg_k = SoilData.objects.aggregate(avg=Avg('potassium'))['avg'] or 0
        avg_ph = SoilData.objects.aggregate(avg=Avg('ph_level'))['avg'] or 0
        
        return JsonResponse({
            'labels': ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'pH Level'],
            'datasets': [{
                'label': 'Average Values',
                'data': [
                    round(avg_n, 2),
                    round(avg_p, 2),
                    round(avg_k, 2),
                    round(avg_ph, 2)
                ],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                ],
                'borderWidth': 1
            }]
        })


class UserGrowthChartView(LoginRequiredMixin, AnalystRequiredMixin, View):
    """
    API endpoint for user growth chart data
    """
    def get(self, request):
        users = User.objects.annotate(
            date=TruncDate('date_joined')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        labels = [u['date'].strftime('%Y-%m-%d') for u in users]
        counts = [u['count'] for u in users]
        
        # Calculate cumulative
        cumulative = []
        total = 0
        for c in counts:
            total += c
            cumulative.append(total)
        
        return JsonResponse({
            'labels': labels,
            'datasets': [{
                'label': 'Total Users',
                'data': cumulative,
                'borderColor': 'rgb(153, 102, 255)',
                'backgroundColor': 'rgba(153, 102, 255, 0.2)',
                'fill': True,
                'tension': 0.4
            }]
        })


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_analytics_summary(request):
    """
    API endpoint for analytics summary
    """
    if request.user.role not in ['analyst', 'admin']:
        return Response({'error': 'Access denied'}, status=403)
    
    return Response({
        'users': {
            'total': User.objects.count(),
            'farmers': User.objects.filter(role='farmer').count(),
            'buyers': User.objects.filter(role='buyer').count(),
        },
        'crops': {
            'total': FarmerCrop.objects.count(),
            'available': FarmerCrop.objects.filter(status='available').count(),
        },
        'orders': {
            'total': Order.objects.count(),
            'completed': Order.objects.filter(status='completed').count(),
            'revenue': float(Order.objects.filter(
                status='completed'
            ).aggregate(total=Sum('total_amount'))['total'] or 0),
        },
        'predictions': {
            'total': PredictionHistory.objects.count(),
            'by_type': {
                'disease': PredictionHistory.objects.filter(prediction_type='disease').count(),
                'price': PredictionHistory.objects.filter(prediction_type='price').count(),
                'soil': PredictionHistory.objects.filter(prediction_type='soil').count(),
            }
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_model_accuracy(request):
    """
    API endpoint for AI model accuracy metrics
    """
    if request.user.role not in ['analyst', 'admin']:
        return Response({'error': 'Access denied'}, status=403)
    
    metrics = AIModelMetrics.objects.all()
    
    data = []
    for m in metrics:
        data.append({
            'model_type': m.model_type,
            'model_version': m.model_version,
            'accuracy': m.accuracy,
            'total_predictions': m.total_predictions,
            'last_updated': m.last_updated,
        })
    
    return Response({'metrics': data})
