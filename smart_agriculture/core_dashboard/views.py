"""
Core Dashboard Views - Main dashboard and home views
"""
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.db.models import Count, Sum, Q
from django.contrib import messages

from smart_agriculture.accounts.models import User
from smart_agriculture.farmer.models import FarmerCrop, Order
from smart_agriculture.ai_models.models import DiseaseDetectionResult, CropPricePrediction


class HomeView(TemplateView):
    """
    Home page view
    """
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Statistics for homepage
        context['total_farmers'] = User.objects.filter(role='farmer').count()
        context['total_buyers'] = User.objects.filter(role='buyer').count()
        context['total_crops'] = FarmerCrop.objects.filter(status='available').count()
        context['total_orders'] = Order.objects.filter(status='completed').count()
        
        # Featured crops
        context['featured_crops'] = FarmerCrop.objects.filter(
            status='available'
        ).select_related('farmer')[:6]
        
        return context


class AboutView(TemplateView):
    """
    About page view
    """
    template_name = 'about.html'


class DashboardView(LoginRequiredMixin, View):
    """
    Main dashboard view - redirects to role-specific dashboard
    """
    def get(self, request):
        role = request.user.role
        
        if role == 'farmer':
            return redirect('farmer:dashboard')
        elif role == 'buyer':
            return redirect('buyer:dashboard')
        elif role == 'admin':
            return redirect('admin_dashboard')
        elif role == 'analyst':
            return redirect('analytics:dashboard')
        else:
            return redirect('home')


class AdminDashboardView(LoginRequiredMixin, View):
    """
    Admin Dashboard View
    """
    template_name = 'core_dashboard/admin_dashboard.html'
    
    def get(self, request):
        if request.user.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('core_dashboard:dashboard')
        
        context = {}
        
        # User statistics
        context['total_users'] = User.objects.count()
        context['farmers'] = User.objects.filter(role='farmer').count()
        context['buyers'] = User.objects.filter(role='buyer').count()
        context['admins'] = User.objects.filter(role='admin').count()
        context['analysts'] = User.objects.filter(role='analyst').count()
        context['new_users_today'] = 0  # Would need to filter by date_joined
        
        # Crop statistics
        context['total_crops'] = FarmerCrop.objects.count()
        context['available_crops'] = FarmerCrop.objects.filter(status='available').count()
        context['sold_crops'] = FarmerCrop.objects.filter(status='sold').count()
        
        # Order statistics
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(status='pending').count()
        context['completed_orders'] = Order.objects.filter(status='completed').count()
        context['cancelled_orders'] = Order.objects.filter(status='cancelled').count()
        
        # Revenue
        context['total_revenue'] = Order.objects.filter(
            status='completed'
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # AI Predictions
        context['total_predictions'] = (
            DiseaseDetectionResult.objects.count() +
            CropPricePrediction.objects.count()
        )
        
        # Recent users
        context['recent_users'] = User.objects.order_by('-date_joined')[:10]
        
        # Recent orders
        context['recent_orders'] = Order.objects.select_related(
            'buyer', 'farmer', 'crop'
        ).order_by('-created_at')[:10]
        
        return render(request, self.template_name, context)


class AdminUserManagementView(LoginRequiredMixin, View):
    """
    Admin User Management View
    """
    template_name = 'core_dashboard/user_management.html'
    
    def get(self, request):
        if request.user.role != 'admin':
            messages.error(request, 'Access denied.')
            return redirect('core_dashboard:dashboard')
        
        users = User.objects.all().order_by('-date_joined')
        return render(request, self.template_name, {'users': users})


class AdminToggleUserStatusView(LoginRequiredMixin, View):
    """
    Toggle user active status
    """
    def post(self, request, user_id):
        if request.user.role != 'admin':
            messages.error(request, 'Access denied.')
            return redirect('core_dashboard:dashboard')
        
        try:
            user = User.objects.get(id=user_id)
            if user != request.user:  # Prevent self-deactivation
                user.is_active = not user.is_active
                user.save()
                status = 'activated' if user.is_active else 'deactivated'
                messages.success(request, f'User {user.name} has been {status}.')
            else:
                messages.error(request, 'You cannot deactivate your own account.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        
        return redirect('admin_user_management')


class SystemLogsView(LoginRequiredMixin, View):
    """
    View system logs
    """
    template_name = 'core_dashboard/system_logs.html'
    
    def get(self, request):
        if request.user.role not in ['admin', 'analyst']:
            messages.error(request, 'Access denied.')
            return redirect('core_dashboard:dashboard')
        
        from smart_agriculture.analytics.models import DailyActivityLog
        
        logs = DailyActivityLog.objects.select_related('user').order_by('-created_at')[:100]
        return render(request, self.template_name, {'logs': logs})
