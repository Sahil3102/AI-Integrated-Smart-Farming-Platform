"""
Buyer App Models
"""
from django.db import models
from django.conf import settings


class BuyerPreferences(models.Model):
    """
    Model for storing buyer preferences
    """
    buyer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_preferences'
    )
    preferred_crops = models.JSONField(default=list, blank=True)
    preferred_locations = models.JSONField(default=list, blank=True)
    price_range_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    price_range_max = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    prefer_organic = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'buyer_preferences'
    
    def __str__(self):
        return f"Preferences - {self.buyer.name}"


class BuyerAnalytics(models.Model):
    """
    Model for buyer analytics
    """
    buyer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='buyer_analytics'
    )
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_crops_purchased = models.IntegerField(default=0)
    favorite_farmers = models.JSONField(default=list, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'buyer_analytics'
    
    def __str__(self):
        return f"Analytics - {self.buyer.name}"
    
    def update_analytics(self):
        """Update buyer analytics"""
        from smart_agriculture.farmer.models import Order
        
        orders = Order.objects.filter(
            buyer=self.buyer,
            status='completed'
        )
        
        self.total_orders = orders.count()
        self.total_spent = orders.aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0
        
        self.total_crops_purchased = orders.values('crop').distinct().count()
        
        # Get favorite farmers
        farmer_orders = orders.values('farmer').annotate(
            count=models.Count('id')
        ).order_by('-count')[:5]
        
        self.favorite_farmers = [
            {'farmer_id': fo['farmer'], 'order_count': fo['count']}
            for fo in farmer_orders
        ]
        
        self.save()


class CropSearchHistory(models.Model):
    """
    Model for storing crop search history
    """
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history'
    )
    search_query = models.CharField(max_length=255)
    filters_applied = models.JSONField(default=dict, blank=True)
    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crop_search_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Search: {self.search_query} - {self.buyer.name}"


class Wishlist(models.Model):
    """
    Model for buyer wishlist
    """
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    crop = models.ForeignKey(
        'farmer.FarmerCrop',
        on_delete=models.CASCADE,
        related_name='wishlisted_by'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wishlist'
        unique_together = ['buyer', 'crop']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.buyer.name} - {self.crop.name}"
