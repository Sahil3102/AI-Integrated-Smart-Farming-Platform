"""
Analytics App Models
"""
from django.db import models
from django.conf import settings


class SystemAnalytics(models.Model):
    """
    Model for storing system-wide analytics
    """
    date = models.DateField(unique=True)
    
    # User statistics
    total_users = models.IntegerField(default=0)
    new_users_today = models.IntegerField(default=0)
    active_farmers = models.IntegerField(default=0)
    active_buyers = models.IntegerField(default=0)
    
    # Crop statistics
    total_crops_listed = models.IntegerField(default=0)
    crops_sold_today = models.IntegerField(default=0)
    
    # Order statistics
    total_orders = models.IntegerField(default=0)
    orders_today = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    revenue_today = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Prediction statistics
    total_predictions = models.IntegerField(default=0)
    predictions_today = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_analytics'
        ordering = ['-date']
    
    def __str__(self):
        return f"Analytics - {self.date}"


class DailyActivityLog(models.Model):
    """
    Model for logging daily system activities
    """
    ACTIVITY_TYPES = [
        ('user_login', 'User Login'),
        ('crop_listed', 'Crop Listed'),
        ('order_placed', 'Order Placed'),
        ('prediction_made', 'Prediction Made'),
        ('disease_detected', 'Disease Detected'),
        ('price_predicted', 'Price Predicted'),
        ('soil_tested', 'Soil Tested'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        null=True,
        blank=True
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_activity_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.activity_type} - {self.user} - {self.created_at}"


class AIModelPerformance(models.Model):
    """
    Model for tracking AI model performance over time
    """
    MODEL_TYPES = [
        ('disease', 'Disease Detection'),
        ('price', 'Price Prediction'),
        ('soil', 'Soil Recommendation'),
        ('weather', 'Weather Forecast'),
    ]
    
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    date = models.DateField()
    
    # Performance metrics
    total_predictions = models.IntegerField(default=0)
    correct_predictions = models.IntegerField(default=0)
    accuracy = models.FloatField(null=True, blank=True)
    
    # User feedback
    positive_feedback = models.IntegerField(default=0)
    negative_feedback = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_model_performance'
        ordering = ['-date']
        unique_together = ['model_type', 'date']
    
    def __str__(self):
        return f"{self.model_type} - {self.date} - {self.accuracy}%"
    
    def save(self, *args, **kwargs):
        # Calculate accuracy
        if self.total_predictions > 0:
            self.accuracy = (self.correct_predictions / self.total_predictions) * 100
        super().save(*args, **kwargs)


class MarketTrend(models.Model):
    """
    Model for storing market trends and price history
    """
    crop = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    date = models.DateField()
    
    # Price data
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2)
    modal_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Volume data
    total_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_arrivals = models.IntegerField(default=0)
    
    # Market information
    market_name = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'market_trends'
        ordering = ['-date']
        unique_together = ['crop', 'state', 'date', 'market_name']
    
    def __str__(self):
        return f"{self.crop} - {self.state} - {self.date} - ₹{self.avg_price}"
