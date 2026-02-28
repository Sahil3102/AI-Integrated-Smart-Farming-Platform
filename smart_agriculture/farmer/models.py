"""
Farmer App Models
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class FarmerCrop(models.Model):
    """
    Model for farmer's crop listings
    """
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
    ]
    
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='crops'
    )
    name = models.CharField(max_length=100)
    variety = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='crops/', blank=True, null=True)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available'
    )
    harvest_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    quality_grade = models.CharField(max_length=50, blank=True, null=True)
    is_organic = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'farmer_crops'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.farmer.name}"
    
    @property
    def total_value(self):
        return self.price_per_kg * self.quantity_kg


class Order(models.Model):
    """
    Model for crop orders
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_id = models.CharField(max_length=20, unique=True)
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='buyer_orders'
    )
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='farmer_orders'
    )
    crop = models.ForeignKey(
        FarmerCrop, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    
    # Delivery information
    delivery_address = models.TextField()
    delivery_date = models.DateField(blank=True, null=True)
    delivered_on_time = models.BooleanField(default=False)
    
    # Ratings and reviews
    rating = models.IntegerField(blank=True, null=True)
    review = models.TextField(blank=True, null=True)
    quality_rating = models.IntegerField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_id} - {self.crop.name}"
    
    def save(self, *args, **kwargs):
        # Generate order ID if not set
        if not self.order_id:
            self.order_id = self.generate_order_id()
        
        # Calculate total amount
        self.total_amount = self.quantity_kg * self.price_per_kg
        
        # Update completed_at timestamp
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Update farmer's reputation score after order completion
        if self.status == 'completed':
            self.farmer.update_reputation_score()
    
    def generate_order_id(self):
        """Generate unique order ID"""
        import uuid
        return f"ORD{uuid.uuid4().hex[:12].upper()}"


class SalesHistory(models.Model):
    """
    Model for farmer sales history
    """
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sales_history'
    )
    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        related_name='sales_record'
    )
    crop_name = models.CharField(max_length=100)
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2)
    amount_received = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateTimeField()
    buyer_name = models.CharField(max_length=150)
    
    class Meta:
        db_table = 'sales_history'
        ordering = ['-sale_date']
    
    def __str__(self):
        return f"Sale {self.crop_name} - {self.farmer.name}"


class FarmerAnalytics(models.Model):
    """
    Model for farmer analytics data
    """
    farmer = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='analytics'
    )
    total_sales = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_crops_listed = models.IntegerField(default=0)
    total_crops_sold = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0)
    response_rate = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'farmer_analytics'
    
    def __str__(self):
        return f"Analytics - {self.farmer.name}"
    
    def update_analytics(self):
        """Update farmer analytics"""
        orders = Order.objects.filter(
            farmer=self.farmer, 
            status='completed'
        )
        
        self.total_sales = orders.count()
        self.total_revenue = orders.aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0
        
        self.total_crops_listed = FarmerCrop.objects.filter(
            farmer=self.farmer
        ).count()
        
        self.total_crops_sold = orders.values('crop').distinct().count()
        
        avg_rating = orders.filter(rating__isnull=False).aggregate(
            avg=models.Avg('rating')
        )['avg']
        self.average_rating = avg_rating or 0
        
        self.save()


class PredictionHistory(models.Model):
    """
    Model for storing farmer's prediction history
    """
    PREDICTION_TYPES = [
        ('disease', 'Disease Detection'),
        ('price', 'Price Prediction'),
        ('soil', 'Soil Recommendation'),
        ('weather', 'Weather Forecast'),
    ]
    
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='prediction_history'
    )
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    input_data = models.JSONField()
    output_data = models.JSONField()
    confidence_score = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'prediction_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.prediction_type} - {self.farmer.name}"
