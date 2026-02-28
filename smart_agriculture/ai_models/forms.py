"""
AI Models Forms
"""
from django import forms


class DiseaseDetectionForm(forms.Form):
    """Form for disease detection"""
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg',
            'accept': 'image/*'
        }),
        help_text='Upload a clear image of the affected leaf'
    )


class PricePredictionForm(forms.Form):
    """Form for price prediction"""
    CROP_CHOICES = [
        ('', 'Select Crop'),
        ('wheat', 'Wheat'),
        ('rice', 'Rice'),
        ('maize', 'Maize'),
        ('cotton', 'Cotton'),
        ('sugarcane', 'Sugarcane'),
        ('potato', 'Potato'),
        ('tomato', 'Tomato'),
        ('onion', 'Onion'),
        ('soybean', 'Soybean'),
        ('groundnut', 'Groundnut'),
    ]
    
    SEASON_CHOICES = [
        ('', 'Select Season'),
        ('kharif', 'Kharif (Monsoon)'),
        ('rabi', 'Rabi (Winter)'),
        ('zaid', 'Zaid (Summer)'),
    ]
    
    crop = forms.ChoiceField(
        choices=CROP_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500'
        })
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'Enter state name'
        })
    )
    season = forms.ChoiceField(
        choices=SEASON_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500'
        })
    )
    rainfall = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'Annual rainfall in mm (optional)'
        })
    )


class SoilRecommendationForm(forms.Form):
    """Form for soil recommendation"""
    nitrogen = forms.FloatField(
        min_value=0,
        max_value=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'Nitrogen (N) in kg/ha'
        })
    )
    phosphorus = forms.FloatField(
        min_value=0,
        max_value=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'Phosphorus (P) in kg/ha'
        })
    )
    potassium = forms.FloatField(
        min_value=0,
        max_value=500,
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'Potassium (K) in kg/ha'
        })
    )
    ph = forms.FloatField(
        min_value=0,
        max_value=14,
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'pH level (0-14)'
        })
    )
    humidity = forms.FloatField(
        required=False,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'Humidity % (optional)'
        })
    )
    temperature = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'Temperature in °C (optional)'
        })
    )
    rainfall = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'Annual rainfall in mm (optional)'
        })
    )
