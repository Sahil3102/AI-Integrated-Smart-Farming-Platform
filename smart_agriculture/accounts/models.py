"""
Accounts models - Custom User Model with roles
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with role-based authentication
    """
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
        ('admin', 'Admin'),
        ('analyst', 'Analyst'),
    ]
    
    id = models.AutoField(primary_key=True)
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('full name'), max_length=150)
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES, default='farmer')
    phone = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    location = models.CharField(_('location'), max_length=255, blank=True, null=True)
    reputation_score = models.FloatField(_('reputation score'), default=0.0)
    
    # Django required fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'
    
    def __str__(self):
        return f"{self.name} ({self.email})"
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name.split()[0] if self.name else self.email
    
    def is_farmer(self):
        return self.role == 'farmer'
    
    def is_buyer(self):
        return self.role == 'buyer'
    
    def is_admin_user(self):
        return self.role == 'admin'
    
    def is_analyst(self):
        return self.role == 'analyst'
    
    def update_reputation_score(self):
        """Update reputation score based on sales, ratings, and performance"""
        if self.role == 'farmer':
            from smart_agriculture.farmer.models import Order, FarmerCrop
            
            # Get all completed orders for this farmer
            orders = Order.objects.filter(farmer=self, status='completed')
            
            total_sales = orders.count()
            avg_rating = orders.filter(rating__isnull=False).aggregate(
                avg=models.Avg('rating')
            )['avg'] or 0
            
            # Calculate product quality score (based on crop quality ratings)
            product_quality = orders.filter(quality_rating__isnull=False).aggregate(
                avg=models.Avg('quality_rating')
            )['avg'] or 0
            
            # Calculate on-time delivery score
            on_time_delivery = orders.filter(delivered_on_time=True).count()
            on_time_score = (on_time_delivery / total_sales * 10) if total_sales > 0 else 0
            
            # Calculate reputation score using weighted formula
            self.reputation_score = (
                (total_sales * 0.4) +
                (avg_rating * 0.3 * 10) +  # Scale rating to 0-30
                (product_quality * 0.2 * 10) +  # Scale quality to 0-20
                (on_time_score * 0.1)  # Scale to 0-10
            )
            self.save(update_fields=['reputation_score'])


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Farmer specific fields
    farm_size = models.FloatField(blank=True, null=True, help_text='Farm size in acres')
    farm_type = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.IntegerField(blank=True, null=True)
    
    # Buyer specific fields
    company_name = models.CharField(max_length=200, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile of {self.user.name}"


class PasswordResetToken(models.Model):
    """
    Store password reset tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_tokens'
    
    def is_valid(self):
        return not self.used and timezone.now() < self.expires_at
