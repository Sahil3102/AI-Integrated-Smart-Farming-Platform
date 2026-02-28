"""
Buyer Views - Class-based views for buyer dashboard
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    View, ListView, DetailView, TemplateView, CreateView
)
from django.db.models import Q, Avg
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from smart_agriculture.farmer.models import FarmerCrop, Order
from smart_agriculture.farmer.forms import BuyCropForm
from .models import BuyerPreferences, BuyerAnalytics, CropSearchHistory, Wishlist


class BuyerRequiredMixin(UserPassesTestMixin):
    """Mixin to check if user is a buyer"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'buyer'
    
    def handle_no_permission(self):
        messages.error(self.request, 'You must be a buyer to access this page.')
        return redirect('core_dashboard:dashboard')


class BuyerDashboardView(LoginRequiredMixin, BuyerRequiredMixin, TemplateView):
    """
    Buyer Dashboard View
    """
    template_name = 'buyer/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get order statistics
        context['total_orders'] = Order.objects.filter(buyer=user).count()
        context['pending_orders'] = Order.objects.filter(
            buyer=user, 
            status__in=['pending', 'confirmed']
        )
        
        # Get completed orders
        completed_orders = Order.objects.filter(buyer=user, status='completed')
        context['completed_orders'] = completed_orders[:5]
        context['total_spent'] = sum(
            order.total_amount for order in completed_orders
        )
        
        # Get recommended crops
        context['recommended_crops'] = FarmerCrop.objects.filter(
            status='available'
        ).select_related('farmer')[:6]
        
        # Get wishlist
        context['wishlist'] = Wishlist.objects.filter(buyer=user)[:5]
        
        # Get or create analytics
        analytics, _ = BuyerAnalytics.objects.get_or_create(buyer=user)
        context['analytics'] = analytics
        
        return context


class BrowseCropsView(ListView):
    """
    Browse all available crops
    """
    model = FarmerCrop
    template_name = 'buyer/browse_crops.html'
    context_object_name = 'crops'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = FarmerCrop.objects.filter(
            status='available'
        ).select_related('farmer')
        
        # Search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(variety__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Location filter
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(
                Q(location__icontains=location) |
                Q(farmer__location__icontains=location)
            )
        
        # Price filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price_per_kg__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_kg__lte=max_price)
        
        # Organic filter
        organic = self.request.GET.get('organic')
        if organic == 'true':
            queryset = queryset.filter(is_organic=True)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by == 'price_low':
            queryset = queryset.order_by('price_per_kg')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price_per_kg')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')
        
        # Save search history if user is authenticated and searching
        if self.request.user.is_authenticated and self.request.user.role == 'buyer' and search:
            CropSearchHistory.objects.create(
                buyer=self.request.user,
                search_query=search,
                filters_applied={
                    'location': location,
                    'min_price': min_price,
                    'max_price': max_price,
                    'organic': organic
                },
                results_count=queryset.count()
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['location'] = self.request.GET.get('location', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['organic'] = self.request.GET.get('organic', '')
        context['sort_by'] = self.request.GET.get('sort', '-created_at')
        return context


class CropDetailView(DetailView):
    """
    View crop details
    """
    model = FarmerCrop
    template_name = 'buyer/crop_detail.html'
    context_object_name = 'crop'
    
    def get_queryset(self):
        return FarmerCrop.objects.select_related('farmer')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        crop = self.object
        
        # Get farmer's other crops
        context['farmer_other_crops'] = FarmerCrop.objects.filter(
            farmer=crop.farmer,
            status='available'
        ).exclude(id=crop.id)[:4]
        
        # Check if in wishlist
        if self.request.user.is_authenticated and self.request.user.role == 'buyer':
            context['in_wishlist'] = Wishlist.objects.filter(
                buyer=self.request.user,
                crop=crop
            ).exists()
        
        # Get farmer's reputation
        context['farmer_reputation'] = crop.farmer.reputation_score
        
        # Get farmer's completed orders count
        context['farmer_sales'] = Order.objects.filter(
            farmer=crop.farmer,
            status='completed'
        ).count()
        
        return context


class BuyCropView(LoginRequiredMixin, BuyerRequiredMixin, View):
    """
    View for buying crops
    """
    template_name = 'buyer/buy_crop.html'
    
    def get(self, request, pk):
        crop = get_object_or_404(FarmerCrop, pk=pk, status='available')
        form = BuyCropForm()
        return render(request, self.template_name, {
            'crop': crop,
            'form': form
        })
    
    def post(self, request, pk):
        crop = get_object_or_404(FarmerCrop, pk=pk, status='available')
        form = BuyCropForm(request.POST)
        
        if form.is_valid():
            quantity = form.cleaned_data['quantity_kg']
            
            # Validate quantity
            if quantity > crop.quantity_kg:
                messages.error(request, 'Requested quantity exceeds available stock.')
                return render(request, self.template_name, {
                    'crop': crop,
                    'form': form
                })
            
            # Create order
            order = Order.objects.create(
                buyer=request.user,
                farmer=crop.farmer,
                crop=crop,
                quantity_kg=quantity,
                price_per_kg=crop.price_per_kg,
                delivery_address=form.cleaned_data['delivery_address'],
                status='pending'
            )
            
            # Update crop quantity
            crop.quantity_kg -= quantity
            if crop.quantity_kg == 0:
                crop.status = 'sold'
            crop.save()
            
            messages.success(
                request, 
                f'Order placed successfully! Order ID: {order.order_id}'
            )
            return redirect('buyer:order_history')
        
        return render(request, self.template_name, {
            'crop': crop,
            'form': form
        })


class OrderHistoryView(LoginRequiredMixin, BuyerRequiredMixin, ListView):
    """
    View order history for buyer
    """
    model = Order
    template_name = 'buyer/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(
            buyer=self.request.user
        ).select_related('crop', 'farmer').order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, BuyerRequiredMixin, DetailView):
    """
    View order details
    """
    model = Order
    template_name = 'buyer/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(
            buyer=self.request.user
        ).select_related('crop', 'farmer')


class FarmerProfileView(DetailView):
    """
    View farmer public profile
    """
    model = FarmerCrop
    template_name = 'buyer/farmer_profile.html'
    context_object_name = 'farmer_profile'
    
    def get_object(self):
        from smart_agriculture.accounts.models import User
        farmer_id = self.kwargs.get('farmer_id')
        return get_object_or_404(User, id=farmer_id, role='farmer')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        farmer = self.object
        
        # Get farmer's available crops
        context['farmer_crops'] = FarmerCrop.objects.filter(
            farmer=farmer,
            status='available'
        )
        
        # Get farmer's statistics
        completed_orders = Order.objects.filter(
            farmer=farmer,
            status='completed'
        )
        context['total_sales'] = completed_orders.count()
        context['reputation_score'] = farmer.reputation_score
        
        # Get average rating
        avg_rating = completed_orders.filter(rating__isnull=False).aggregate(
            avg=Avg('rating')
        )['avg']
        context['average_rating'] = avg_rating or 0
        
        return context


class WishlistView(LoginRequiredMixin, BuyerRequiredMixin, ListView):
    """
    View wishlist
    """
    model = Wishlist
    template_name = 'buyer/wishlist.html'
    context_object_name = 'wishlist_items'
    paginate_by = 10
    
    def get_queryset(self):
        return Wishlist.objects.filter(
            buyer=self.request.user
        ).select_related('crop', 'crop__farmer')


class AddToWishlistView(LoginRequiredMixin, BuyerRequiredMixin, View):
    """
    Add crop to wishlist
    """
    def post(self, request, crop_id):
        crop = get_object_or_404(FarmerCrop, id=crop_id)
        
        wishlist_item, created = Wishlist.objects.get_or_create(
            buyer=request.user,
            crop=crop
        )
        
        if created:
            messages.success(request, 'Crop added to wishlist!')
        else:
            messages.info(request, 'Crop is already in your wishlist.')
        
        return redirect('buyer:crop_detail', pk=crop_id)


class RemoveFromWishlistView(LoginRequiredMixin, BuyerRequiredMixin, View):
    """
    Remove crop from wishlist
    """
    def post(self, request, crop_id):
        crop = get_object_or_404(FarmerCrop, id=crop_id)
        
        Wishlist.objects.filter(
            buyer=request.user,
            crop=crop
        ).delete()
        
        messages.success(request, 'Crop removed from wishlist.')
        return redirect('buyer:wishlist')


# API Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_buyer_dashboard_stats(request):
    """
    API endpoint for buyer dashboard statistics
    """
    if request.user.role != 'buyer':
        return Response({'error': 'Access denied'}, status=403)
    
    user = request.user
    
    # Order statistics
    total_orders = Order.objects.filter(buyer=user).count()
    pending_orders = Order.objects.filter(
        buyer=user, 
        status__in=['pending', 'confirmed']
    ).count()
    
    # Spending statistics
    completed_orders = Order.objects.filter(buyer=user, status='completed')
    total_spent = completed_orders.aggregate(
        total=models.Sum('total_amount')
    )['total'] or 0
    
    # Wishlist count
    wishlist_count = Wishlist.objects.filter(buyer=user).count()
    
    return Response({
        'orders': {
            'total': total_orders,
            'pending': pending_orders,
            'completed': completed_orders.count(),
        },
        'spending': {
            'total_spent': float(total_spent),
        },
        'wishlist_count': wishlist_count,
    })


@api_view(['GET'])
def api_browse_crops(request):
    """
    API endpoint to browse crops
    """
    queryset = FarmerCrop.objects.filter(status='available')
    
    # Apply filters
    search = request.GET.get('search')
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(variety__icontains=search)
        )
    
    location = request.GET.get('location')
    if location:
        queryset = queryset.filter(location__icontains=location)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        queryset = queryset.filter(price_per_kg__gte=min_price)
    if max_price:
        queryset = queryset.filter(price_per_kg__lte=max_price)
    
    crops_data = []
    for crop in queryset.select_related('farmer')[:50]:
        crops_data.append({
            'id': crop.id,
            'name': crop.name,
            'variety': crop.variety,
            'price_per_kg': float(crop.price_per_kg),
            'quantity_kg': float(crop.quantity_kg),
            'location': crop.location,
            'is_organic': crop.is_organic,
            'farmer': {
                'id': crop.farmer.id,
                'name': crop.farmer.name,
                'reputation_score': crop.farmer.reputation_score,
            },
            'image': crop.image.url if crop.image else None,
        })
    
    return Response({'crops': crops_data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_buy_crop(request):
    """
    API endpoint to buy crop
    """
    if request.user.role != 'buyer':
        return Response({'error': 'Access denied'}, status=403)
    
    crop_id = request.data.get('crop_id')
    quantity = request.data.get('quantity_kg')
    delivery_address = request.data.get('delivery_address')
    
    if not all([crop_id, quantity, delivery_address]):
        return Response(
            {'error': 'crop_id, quantity_kg, and delivery_address are required'},
            status=400
        )
    
    try:
        crop = FarmerCrop.objects.get(id=crop_id, status='available')
    except FarmerCrop.DoesNotExist:
        return Response({'error': 'Crop not found or not available'}, status=404)
    
    if float(quantity) > float(crop.quantity_kg):
        return Response({'error': 'Quantity exceeds available stock'}, status=400)
    
    order = Order.objects.create(
        buyer=request.user,
        farmer=crop.farmer,
        crop=crop,
        quantity_kg=quantity,
        price_per_kg=crop.price_per_kg,
        delivery_address=delivery_address,
        status='pending'
    )
    
    # Update crop quantity
    crop.quantity_kg -= float(quantity)
    if crop.quantity_kg <= 0:
        crop.status = 'sold'
    crop.save()
    
    return Response({
        'message': 'Order placed successfully',
        'order': {
            'order_id': order.order_id,
            'total_amount': float(order.total_amount),
            'status': order.status,
        }
    }, status=201)
