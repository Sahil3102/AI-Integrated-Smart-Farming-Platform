"""
Farmer Views - Class-based views for farmer dashboard
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    View, ListView, CreateView, UpdateView, 
    DetailView, TemplateView, DeleteView
)
from django.db.models import Sum, Avg, Count
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import FarmerCrop, Order, SalesHistory, PredictionHistory, FarmerAnalytics
from .forms import FarmerCropForm, OrderStatusUpdateForm


class FarmerRequiredMixin(UserPassesTestMixin):
    """Mixin to check if user is a farmer"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'farmer'
    
    def handle_no_permission(self):
        messages.error(self.request, 'You must be a farmer to access this page.')
        return redirect('core_dashboard:dashboard')


class FarmerDashboardView(LoginRequiredMixin, FarmerRequiredMixin, TemplateView):
    """
    Farmer Dashboard View
    """
    template_name = 'farmer/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get farmer's crops
        context['crops'] = FarmerCrop.objects.filter(farmer=user)[:5]
        context['total_crops'] = FarmerCrop.objects.filter(farmer=user).count()
        
        # Get orders
        context['pending_orders'] = Order.objects.filter(
            farmer=user, 
            status__in=['pending', 'confirmed']
        )[:5]
        context['total_orders'] = Order.objects.filter(farmer=user).count()
        
        # Get sales statistics
        completed_orders = Order.objects.filter(farmer=user, status='completed')
        context['total_sales'] = completed_orders.count()
        context['total_revenue'] = completed_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Get reputation score
        context['reputation_score'] = user.reputation_score
        
        # Get recent predictions
        context['recent_predictions'] = PredictionHistory.objects.filter(
            farmer=user
        )[:5]
        
        # Get or create analytics
        analytics, _ = FarmerAnalytics.objects.get_or_create(farmer=user)
        context['analytics'] = analytics
        
        return context


class CropListView(LoginRequiredMixin, FarmerRequiredMixin, ListView):
    """
    List all farmer's crops
    """
    model = FarmerCrop
    template_name = 'farmer/crop_list.html'
    context_object_name = 'crops'
    paginate_by = 10
    
    def get_queryset(self):
        return FarmerCrop.objects.filter(farmer=self.request.user)


class CropCreateView(LoginRequiredMixin, FarmerRequiredMixin, CreateView):
    """
    Create new crop listing
    """
    model = FarmerCrop
    form_class = FarmerCropForm
    template_name = 'farmer/crop_form.html'
    success_url = reverse_lazy('farmer:crop_list')
    
    def form_valid(self, form):
        form.instance.farmer = self.request.user
        messages.success(self.request, 'Crop listing created successfully!')
        return super().form_valid(form)


class CropUpdateView(LoginRequiredMixin, FarmerRequiredMixin, UpdateView):
    """
    Update crop listing
    """
    model = FarmerCrop
    form_class = FarmerCropForm
    template_name = 'farmer/crop_form.html'
    success_url = reverse_lazy('farmer:crop_list')
    
    def get_queryset(self):
        return FarmerCrop.objects.filter(farmer=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Crop listing updated successfully!')
        return super().form_valid(form)


class CropDeleteView(LoginRequiredMixin, FarmerRequiredMixin, DeleteView):
    """
    Delete crop listing
    """
    model = FarmerCrop
    template_name = 'farmer/crop_confirm_delete.html'
    success_url = reverse_lazy('farmer:crop_list')
    
    def get_queryset(self):
        return FarmerCrop.objects.filter(farmer=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Crop listing deleted successfully!')
        return super().delete(request, *args, **kwargs)


class OrderListView(LoginRequiredMixin, FarmerRequiredMixin, ListView):
    """
    List all orders received by farmer
    """
    model = Order
    template_name = 'farmer/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(farmer=self.request.user)


class OrderDetailView(LoginRequiredMixin, FarmerRequiredMixin, DetailView):
    """
    View order details
    """
    model = Order
    template_name = 'farmer/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(farmer=self.request.user)


class OrderStatusUpdateView(LoginRequiredMixin, FarmerRequiredMixin, UpdateView):
    """
    Update order status
    """
    model = Order
    form_class = OrderStatusUpdateForm
    template_name = 'farmer/order_status_update.html'
    
    def get_queryset(self):
        return Order.objects.filter(farmer=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('farmer:order_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        order = form.save(commit=False)
        
        # Update delivered_on_time if status is delivered
        if order.status == 'delivered' and order.delivery_date:
            order.delivered_on_time = order.delivery_date >= timezone.now().date()
        
        order.save()
        
        # Create sales history if order is completed
        if order.status == 'completed':
            SalesHistory.objects.get_or_create(
                order=order,
                defaults={
                    'farmer': order.farmer,
                    'crop_name': order.crop.name,
                    'quantity_sold': order.quantity_kg,
                    'amount_received': order.total_amount,
                    'sale_date': timezone.now(),
                    'buyer_name': order.buyer.name
                }
            )
        
        messages.success(self.request, 'Order status updated successfully!')
        return super().form_valid(form)


class SalesHistoryView(LoginRequiredMixin, FarmerRequiredMixin, ListView):
    """
    View sales history
    """
    model = SalesHistory
    template_name = 'farmer/sales_history.html'
    context_object_name = 'sales'
    paginate_by = 10
    
    def get_queryset(self):
        return SalesHistory.objects.filter(farmer=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Calculate statistics
        sales = SalesHistory.objects.filter(farmer=user)
        context['total_sales'] = sales.count()
        context['total_revenue'] = sales.aggregate(
            total=Sum('amount_received')
        )['total'] or 0
        context['total_quantity'] = sales.aggregate(
            total=Sum('quantity_sold')
        )['total'] or 0
        
        return context


class PredictionHistoryView(LoginRequiredMixin, FarmerRequiredMixin, ListView):
    """
    View prediction history
    """
    model = PredictionHistory
    template_name = 'farmer/prediction_history.html'
    context_object_name = 'predictions'
    paginate_by = 10
    
    def get_queryset(self):
        return PredictionHistory.objects.filter(farmer=self.request.user)


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_farmer_dashboard_stats(request):
    """
    API endpoint for farmer dashboard statistics
    """
    if request.user.role != 'farmer':
        return Response({'error': 'Access denied'}, status=403)
    
    user = request.user
    
    # Crop statistics
    total_crops = FarmerCrop.objects.filter(farmer=user).count()
    available_crops = FarmerCrop.objects.filter(farmer=user, status='available').count()
    
    # Order statistics
    total_orders = Order.objects.filter(farmer=user).count()
    pending_orders = Order.objects.filter(farmer=user, status='pending').count()
    completed_orders = Order.objects.filter(farmer=user, status='completed')
    
    # Sales statistics
    total_sales = completed_orders.count()
    total_revenue = completed_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Reputation
    reputation_score = user.reputation_score
    
    return Response({
        'crops': {
            'total': total_crops,
            'available': available_crops,
        },
        'orders': {
            'total': total_orders,
            'pending': pending_orders,
            'completed': total_sales,
        },
        'sales': {
            'total_orders': total_sales,
            'total_revenue': float(total_revenue),
        },
        'reputation_score': reputation_score,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_add_crop(request):
    """
    API endpoint to add a new crop
    """
    if request.user.role != 'farmer':
        return Response({'error': 'Access denied'}, status=403)
    
    data = request.data
    required_fields = ['name', 'price_per_kg', 'quantity_kg']
    
    for field in required_fields:
        if field not in data:
            return Response(
                {'error': f'{field} is required'}, 
                status=400
            )
    
    crop = FarmerCrop.objects.create(
        farmer=request.user,
        name=data['name'],
        variety=data.get('variety', ''),
        description=data.get('description', ''),
        price_per_kg=data['price_per_kg'],
        quantity_kg=data['quantity_kg'],
        location=data.get('location', ''),
        quality_grade=data.get('quality_grade', ''),
        is_organic=data.get('is_organic', False),
    )
    
    return Response({
        'message': 'Crop added successfully',
        'crop': {
            'id': crop.id,
            'name': crop.name,
            'price_per_kg': float(crop.price_per_kg),
            'quantity_kg': float(crop.quantity_kg),
        }
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_farmer_orders(request):
    """
    API endpoint to get farmer's orders
    """
    if request.user.role != 'farmer':
        return Response({'error': 'Access denied'}, status=403)
    
    orders = Order.objects.filter(farmer=request.user)
    
    data = []
    for order in orders:
        data.append({
            'order_id': order.order_id,
            'buyer': order.buyer.name,
            'crop': order.crop.name,
            'quantity_kg': float(order.quantity_kg),
            'total_amount': float(order.total_amount),
            'status': order.status,
            'created_at': order.created_at,
        })
    
    return Response({'orders': data})
