"""
AI Models App Models - Store AI prediction results and model metadata
"""
from django.db import models
from django.conf import settings


class DiseaseDetectionResult(models.Model):
    """
    Model for storing plant disease detection results
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disease_detections'
    )
    image = models.ImageField(upload_to='disease_detection/')
    disease_name = models.CharField(max_length=200)
    confidence_score = models.FloatField()
    treatment_suggestion = models.TextField()
    affected_areas = models.JSONField(default=list, blank=True)
    severity_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='low'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'disease_detection_results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.disease_name} - {self.user.name}"


class CropPricePrediction(models.Model):
    """
    Model for storing crop price predictions
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='price_predictions',
        null=True,
        blank=True
    )
    crop_name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    season = models.CharField(max_length=50)
    rainfall = models.FloatField(null=True, blank=True)
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_trend = models.CharField(
        max_length=20,
        choices=[
            ('increasing', 'Increasing'),
            ('decreasing', 'Decreasing'),
            ('stable', 'Stable'),
        ],
        default='stable'
    )
    confidence_interval = models.JSONField(default=dict, blank=True)
    historical_data = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crop_price_predictions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.crop_name} - ₹{self.predicted_price}"


class SoilRecommendation(models.Model):
    """
    Model for storing soil-based crop recommendations
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='soil_recommendations',
        null=True,
        blank=True
    )
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    ph_level = models.FloatField()
    # Optional additional parameters
    humidity = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    rainfall = models.FloatField(null=True, blank=True)
    
    recommended_crop = models.CharField(max_length=100)
    confidence_score = models.FloatField()
    alternative_crops = models.JSONField(default=list, blank=True)
    fertilizer_suggestion = models.TextField()
    soil_health_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'soil_recommendations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recommended_crop} - N:{self.nitrogen} P:{self.phosphorus} K:{self.potassium}"


class WeatherForecast(models.Model):
    """
    Model for storing weather forecasts
    """
    location = models.CharField(max_length=255)
    forecast_date = models.DateField()
    temperature_max = models.FloatField()
    temperature_min = models.FloatField()
    humidity = models.FloatField()
    rainfall_probability = models.FloatField()
    rainfall_amount = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    weather_condition = models.CharField(max_length=50)
    uv_index = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'weather_forecasts'
        ordering = ['-forecast_date']
        unique_together = ['location', 'forecast_date']
    
    def __str__(self):
        return f"{self.location} - {self.forecast_date}"


class AIModelMetrics(models.Model):
    """
    Model for tracking AI model performance metrics
    """
    MODEL_TYPES = [
        ('disease', 'Disease Detection'),
        ('price', 'Price Prediction'),
        ('soil', 'Soil Recommendation'),
        ('weather', 'Weather Forecast'),
    ]
    
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    model_version = models.CharField(max_length=50)
    accuracy = models.FloatField()
    precision = models.FloatField(null=True, blank=True)
    recall = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True)  # Mean Absolute Error
    rmse = models.FloatField(null=True, blank=True)  # Root Mean Square Error
    total_predictions = models.IntegerField(default=0)
    correct_predictions = models.IntegerField(default=0)
    training_date = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ai_model_metrics'
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"{self.model_type} - v{self.model_version} - {self.accuracy:.2%}"
    
    @property
    def current_accuracy(self):
        if self.total_predictions > 0:
            return (self.correct_predictions / self.total_predictions) * 100
        return 0


class ModelTrainingLog(models.Model):
    """
    Model for tracking model training history
    """
    model_type = models.CharField(max_length=20, choices=AIModelMetrics.MODEL_TYPES)
    training_start = models.DateTimeField()
    training_end = models.DateTimeField(null=True, blank=True)
    dataset_size = models.IntegerField()
    epochs = models.IntegerField(null=True, blank=True)
    batch_size = models.IntegerField(null=True, blank=True)
    final_loss = models.FloatField(null=True, blank=True)
    final_accuracy = models.FloatField(null=True, blank=True)
    validation_accuracy = models.FloatField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('running', 'Running'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='running'
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'model_training_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.model_type} - {self.status} - {self.training_start}"
