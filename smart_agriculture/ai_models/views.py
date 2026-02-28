"""
AI Models Views - API endpoints for AI predictions
"""
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.contrib import messages

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .ml_models import (
    detect_disease, predict_price, 
    recommend_crop, get_weather_forecast, get_current_weather
)
from .models import (
    DiseaseDetectionResult, CropPricePrediction,
    SoilRecommendation, WeatherForecast
)
from smart_agriculture.farmer.models import PredictionHistory


class DiseaseDetectionView(LoginRequiredMixin, View):
    """
    View for disease detection page
    """
    template_name = 'ai_models/disease_detection.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        if 'image' not in request.FILES:
            messages.error(request, 'Please upload an image.')
            return render(request, self.template_name)
        
        image = request.FILES['image']
        
        # Save uploaded image
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'disease_uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        image_path = os.path.join(upload_dir, image.name)
        with open(image_path, 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        # Perform detection
        result = detect_disease(image_path)
        
        # Save result to database
        detection_result = DiseaseDetectionResult.objects.create(
            user=request.user,
            image=f'disease_uploads/{image.name}',
            disease_name=result['disease_name'],
            confidence_score=result['confidence_score'],
            treatment_suggestion=result['treatment_suggestion'],
            severity_level=result['severity_level']
        )
        
        # Save to prediction history
        PredictionHistory.objects.create(
            farmer=request.user,
            prediction_type='disease',
            input_data={'image': image.name},
            output_data=result,
            confidence_score=result['confidence_score']
        )
        
        return render(request, self.template_name, {
            'result': result,
            'image_url': f'{settings.MEDIA_URL}disease_uploads/{image.name}'
        })


class PricePredictionView(LoginRequiredMixin, View):
    """
    View for price prediction page
    """
    template_name = 'ai_models/price_prediction.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        crop = request.POST.get('crop')
        state = request.POST.get('state')
        season = request.POST.get('season')
        rainfall = request.POST.get('rainfall')
        
        if not all([crop, state, season]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, self.template_name)
        
        # Convert rainfall to float if provided
        rainfall_val = float(rainfall) if rainfall else None
        
        # Perform prediction
        result = predict_price(crop, state, season, rainfall_val)
        
        # Save result to database
        CropPricePrediction.objects.create(
            user=request.user,
            crop_name=crop,
            state=state,
            season=season,
            rainfall=rainfall_val,
            predicted_price=result['predicted_price'],
            price_trend=result['price_trend'],
            confidence_interval=result['confidence_interval'],
            historical_data=result['historical_data']
        )
        
        # Save to prediction history
        PredictionHistory.objects.create(
            farmer=request.user,
            prediction_type='price',
            input_data={
                'crop': crop,
                'state': state,
                'season': season,
                'rainfall': rainfall_val
            },
            output_data=result,
        )
        
        return render(request, self.template_name, {'result': result})


class SoilRecommendationView(LoginRequiredMixin, View):
    """
    View for soil recommendation page
    """
    template_name = 'ai_models/soil_recommendation.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        try:
            nitrogen = float(request.POST.get('nitrogen', 0))
            phosphorus = float(request.POST.get('phosphorus', 0))
            potassium = float(request.POST.get('potassium', 0))
            ph = float(request.POST.get('ph', 7.0))
            humidity = request.POST.get('humidity')
            temperature = request.POST.get('temperature')
            rainfall = request.POST.get('rainfall')
            
            # Optional parameters
            humidity_val = float(humidity) if humidity else None
            temperature_val = float(temperature) if temperature else None
            rainfall_val = float(rainfall) if rainfall else None
            
            # Perform recommendation
            result = recommend_crop(
                nitrogen, phosphorus, potassium, ph,
                humidity_val, temperature_val, rainfall_val
            )
            
            # Save result to database
            SoilRecommendation.objects.create(
                user=request.user,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                ph_level=ph,
                humidity=humidity_val,
                temperature=temperature_val,
                rainfall=rainfall_val,
                recommended_crop=result['recommended_crop'],
                confidence_score=result['confidence_score'],
                alternative_crops=result['alternative_crops'],
                fertilizer_suggestion=result['fertilizer_recommendation'],
                soil_health_score=result['soil_health_score']
            )
            
            # Save to prediction history
            PredictionHistory.objects.create(
                farmer=request.user,
                prediction_type='soil',
                input_data={
                    'N': nitrogen,
                    'P': phosphorus,
                    'K': potassium,
                    'pH': ph,
                    'humidity': humidity_val,
                    'temperature': temperature_val,
                    'rainfall': rainfall_val
                },
                output_data=result,
                confidence_score=result['confidence_score']
            )
            
            return render(request, self.template_name, {'result': result})
            
        except ValueError as e:
            messages.error(request, 'Please enter valid numeric values.')
            return render(request, self.template_name)


class WeatherForecastView(LoginRequiredMixin, View):
    """
    View for weather forecast page
    """
    template_name = 'ai_models/weather_forecast.html'
    
    def get(self, request):
        location = request.GET.get('location', request.user.location or 'New Delhi')
        days = int(request.GET.get('days', 7))
        
        # Get forecast
        forecast = get_weather_forecast(location, days)
        
        # Get current weather
        current = get_current_weather(location)
        
        return render(request, self.template_name, {
            'forecast': forecast,
            'current': current,
            'location': location
        })


# API Endpoints
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_disease_detection(request):
    """
    API endpoint for disease detection
    """
    if 'image' not in request.FILES:
        return Response(
            {'error': 'No image provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    image = request.FILES['image']
    
    # Save uploaded image
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'disease_uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    image_path = os.path.join(upload_dir, image.name)
    with open(image_path, 'wb+') as destination:
        for chunk in image.chunks():
            destination.write(chunk)
    
    # Perform detection
    result = detect_disease(image_path)
    
    # Save result
    DiseaseDetectionResult.objects.create(
        user=request.user,
        image=f'disease_uploads/{image.name}',
        disease_name=result['disease_name'],
        confidence_score=result['confidence_score'],
        treatment_suggestion=result['treatment_suggestion'],
        severity_level=result['severity_level']
    )
    
    return Response({
        'message': 'Disease detection completed',
        'result': result
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_price_prediction(request):
    """
    API endpoint for price prediction
    """
    crop = request.data.get('crop')
    state = request.data.get('state')
    season = request.data.get('season')
    rainfall = request.data.get('rainfall')
    
    if not all([crop, state, season]):
        return Response(
            {'error': 'crop, state, and season are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    rainfall_val = float(rainfall) if rainfall else None
    
    result = predict_price(crop, state, season, rainfall_val)
    
    # Save result
    CropPricePrediction.objects.create(
        user=request.user,
        crop_name=crop,
        state=state,
        season=season,
        rainfall=rainfall_val,
        predicted_price=result['predicted_price'],
        price_trend=result['price_trend'],
        confidence_interval=result['confidence_interval'],
        historical_data=result['historical_data']
    )
    
    return Response({
        'message': 'Price prediction completed',
        'result': result
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_soil_recommendation(request):
    """
    API endpoint for soil recommendation
    """
    try:
        nitrogen = float(request.data.get('nitrogen', 0))
        phosphorus = float(request.data.get('phosphorus', 0))
        potassium = float(request.data.get('potassium', 0))
        ph = float(request.data.get('ph', 7.0))
        humidity = request.data.get('humidity')
        temperature = request.data.get('temperature')
        rainfall = request.data.get('rainfall')
        
        humidity_val = float(humidity) if humidity else None
        temperature_val = float(temperature) if temperature else None
        rainfall_val = float(rainfall) if rainfall else None
        
        result = recommend_crop(
            nitrogen, phosphorus, potassium, ph,
            humidity_val, temperature_val, rainfall_val
        )
        
        # Save result
        SoilRecommendation.objects.create(
            user=request.user,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            ph_level=ph,
            humidity=humidity_val,
            temperature=temperature_val,
            rainfall=rainfall_val,
            recommended_crop=result['recommended_crop'],
            confidence_score=result['confidence_score'],
            alternative_crops=result['alternative_crops'],
            fertilizer_suggestion=result['fertilizer_recommendation'],
            soil_health_score=result['soil_health_score']
        )
        
        return Response({
            'message': 'Soil recommendation completed',
            'result': result
        })
        
    except ValueError as e:
        return Response(
            {'error': 'Invalid numeric values provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_weather_forecast(request):
    """
    API endpoint for weather forecast
    """
    location = request.GET.get('location', request.user.location or 'New Delhi')
    days = int(request.GET.get('days', 7))
    
    forecast = get_weather_forecast(location, days)
    current = get_current_weather(location)
    
    return Response({
        'location': location,
        'current_weather': current,
        'forecast': forecast
    })
