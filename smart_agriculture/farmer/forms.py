"""
Farmer Forms
"""
from django import forms
from .models import FarmerCrop, Order


class FarmerCropForm(forms.ModelForm):
    """
    Form for adding/editing farmer crops
    """
    class Meta:
        model = FarmerCrop
        fields = ['name', 'variety', 'description', 'price_per_kg', 'quantity_kg', 
                  'image', 'harvest_date', 'location', 'quality_grade', 'is_organic']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'placeholder': 'Crop name (e.g., Wheat, Rice)'
            }),
            'variety': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'placeholder': 'Variety (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'rows': 3,
                'placeholder': 'Describe your crop...'
            }),
            'price_per_kg': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'placeholder': 'Price per kg',
                'min': '0',
                'step': '0.01'
            }),
            'quantity_kg': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'placeholder': 'Available quantity in kg',
                'min': '0',
                'step': '0.01'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg',
                'accept': 'image/*'
            }),
            'harvest_date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'placeholder': 'Crop location'
            }),
            'quality_grade': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500'
            }, choices=[
                ('', 'Select Grade'),
                ('A+', 'Grade A+ (Premium)'),
                ('A', 'Grade A (Excellent)'),
                ('B', 'Grade B (Good)'),
                ('C', 'Grade C (Average)'),
            ]),
            'is_organic': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-5 w-5 text-green-600'
            }),
        }


class OrderStatusUpdateForm(forms.ModelForm):
    """
    Form for updating order status
    """
    class Meta:
        model = Order
        fields = ['status', 'delivery_date']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500'
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'type': 'date'
            }),
        }


class OrderReviewForm(forms.ModelForm):
    """
    Form for buyers to review orders
    """
    class Meta:
        model = Order
        fields = ['rating', 'review', 'quality_rating']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'min': '1',
                'max': '5',
                'placeholder': 'Rate 1-5'
            }),
            'review': forms.Textarea(attrs={
                'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'rows': 4,
                'placeholder': 'Write your review...'
            }),
            'quality_rating': forms.NumberInput(attrs={
                'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
                'min': '1',
                'max': '5',
                'placeholder': 'Quality rating 1-5'
            }),
        }


class BuyCropForm(forms.Form):
    """
    Form for buying crops
    """
    quantity_kg = forms.DecimalField(
        min_value=0.1,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-input w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'placeholder': 'Quantity in kg',
            'min': '0.1',
            'step': '0.1'
        })
    )
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500',
            'rows': 3,
            'placeholder': 'Enter delivery address'
        })
    )
