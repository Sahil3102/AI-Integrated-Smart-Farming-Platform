"""
Accounts Views - Class-based views for authentication
"""
import secrets
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import View, CreateView, FormView, TemplateView, UpdateView
from django.conf import settings

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .forms import (
    UserRegistrationForm, UserLoginForm, UserProfileForm, 
    ExtendedProfileForm, PasswordResetRequestForm, PasswordResetConfirmForm
)
from .models import User, UserProfile, PasswordResetToken


class RegisterView(CreateView):
    """
    User registration view
    """
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save()
        # Create user profile
        UserProfile.objects.create(user=user)
        messages.success(self.request, 'Registration successful! Please log in.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class LoginView(FormView):
    """
    User login view
    """
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    
    def get_success_url(self):
        """Redirect based on user role"""
        role_urls = settings.ROLE_REDIRECT_URLS
        return role_urls.get(self.request.user.role, '/dashboard/')
    
    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, email=email, password=password)
        
        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {user.name}!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid email or password.')
            return self.form_invalid(form)


class LogoutView(LoginRequiredMixin, View):
    """
    User logout view
    """
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('home')


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    User profile view
    """
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['profile'], _ = UserProfile.objects.get_or_create(user=user)
        return context


class ProfileUpdateView(LoginRequiredMixin, View):
    """
    Update user profile view
    """
    template_name = 'accounts/profile_edit.html'
    
    def get(self, request):
        user_form = UserProfileForm(instance=request.user)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile_form = ExtendedProfileForm(instance=profile)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })
    
    def post(self, request):
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile_form = ExtendedProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })


class PasswordResetRequestView(FormView):
    """
    Password reset request view
    """
    template_name = 'accounts/password_reset_request.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            # Generate token
            token = secrets.token_urlsafe(32)
            expires_at = timezone.now() + timedelta(hours=24)
            
            PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            # In production, send email here
            messages.success(
                self.request, 
                'Password reset link has been sent to your email.'
            )
        except User.DoesNotExist:
            # Don't reveal if email exists
            messages.success(
                self.request, 
                'Password reset link has been sent to your email.'
            )
        
        return super().form_valid(form)


class PasswordResetConfirmView(FormView):
    """
    Password reset confirmation view
    """
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy('login')
    
    def dispatch(self, request, *args, **kwargs):
        self.token = kwargs.get('token')
        try:
            self.reset_token = PasswordResetToken.objects.get(
                token=self.token,
                used=False,
                expires_at__gt=timezone.now()
            )
        except PasswordResetToken.DoesNotExist:
            messages.error(request, 'Invalid or expired reset link.')
            return redirect('password_reset_request')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        new_password = form.cleaned_data['new_password']
        user = self.reset_token.user
        user.set_password(new_password)
        user.save()
        
        self.reset_token.used = True
        self.reset_token.save()
        
        messages.success(self.request, 'Password reset successful! Please log in.')
        return super().form_valid(form)


# API Views for JWT Authentication
@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """
    API endpoint for user registration
    """
    data = request.data
    required_fields = ['email', 'name', 'password', 'role']
    
    for field in required_fields:
        if field not in data:
            return Response(
                {'error': f'{field} is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if User.objects.filter(email=data['email']).exists():
        return Response(
            {'error': 'Email already registered'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(
        email=data['email'],
        name=data['name'],
        password=data['password'],
        role=data['role'],
        phone=data.get('phone', ''),
        location=data.get('location', '')
    )
    
    # Create user profile
    UserProfile.objects.create(user=user)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Registration successful',
        'user': {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    API endpoint for user login
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, email=email, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'reputation_score': user.reputation_score,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """
    API endpoint for user logout
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'})
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    """
    API endpoint to get user profile
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    return Response({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role,
        'phone': user.phone,
        'location': user.location,
        'reputation_score': user.reputation_score,
        'date_joined': user.date_joined,
        'profile': {
            'avatar': profile.avatar.url if profile.avatar else None,
            'bio': profile.bio,
            'address': profile.address,
            'city': profile.city,
            'state': profile.state,
            'country': profile.country,
            'farm_size': profile.farm_size,
            'farm_type': profile.farm_type,
            'years_of_experience': profile.years_of_experience,
            'company_name': profile.company_name,
            'business_type': profile.business_type,
        }
    })
