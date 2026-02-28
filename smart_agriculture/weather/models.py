"""
Weather App Models
"""
from django.db import models
from django.conf import settings


class WeatherLog(models.Model):
    """
    Model for storing weather data logs
    """
    location = models.CharField(max_length=255)
    date = models.DateField()
    
    # Temperature
    temperature_max = models.FloatField()
    temperature_min = models.FloatField()
    temperature_avg = models.FloatField(null=True, blank=True)
    
    # Humidity and precipitation
    humidity = models.FloatField()
    rainfall = models.FloatField(default=0, help_text='Rainfall in mm')
    rainfall_probability = models.FloatField(null=True, blank=True)
    
    # Wind and pressure
    wind_speed = models.FloatField(null=True, blank=True)
    wind_direction = models.CharField(max_length=20, blank=True, null=True)
    pressure = models.FloatField(null=True, blank=True)
    
    # Conditions
    weather_condition = models.CharField(max_length=50)
    uv_index = models.FloatField(null=True, blank=True)
    visibility = models.FloatField(null=True, blank=True)
    
    # Sunrise/Sunset
    sunrise = models.TimeField(null=True, blank=True)
    sunset = models.TimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'weather_logs'
        ordering = ['-date']
        unique_together = ['location', 'date']
    
    def __str__(self):
        return f"{self.location} - {self.date} - {self.weather_condition}"
    
    def save(self, *args, **kwargs):
        # Calculate average temperature
        if self.temperature_max and self.temperature_min and not self.temperature_avg:
            self.temperature_avg = (self.temperature_max + self.temperature_min) / 2
        super().save(*args, **kwargs)


class WeatherAlert(models.Model):
    """
    Model for weather alerts and warnings
    """
    ALERT_TYPES = [
        ('heavy_rain', 'Heavy Rain Warning'),
        ('drought', 'Drought Warning'),
        ('frost', 'Frost Warning'),
        ('heat_wave', 'Heat Wave Warning'),
        ('storm', 'Storm Warning'),
        ('flood', 'Flood Warning'),
        ('strong_wind', 'Strong Wind Warning'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('severe', 'Severe'),
    ]
    
    location = models.CharField(max_length=255)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    issued_at = models.DateTimeField(auto_now_add=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    acknowledged_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='acknowledged_alerts'
    )
    
    class Meta:
        db_table = 'weather_alerts'
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"{self.title} - {self.location}"


class CropWeatherIndex(models.Model):
    """
    Model for storing crop-specific weather indices
    """
    crop = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    date = models.DateField()
    
    # Indices
    growing_degree_days = models.FloatField(null=True, blank=True)
    heat_stress_index = models.FloatField(null=True, blank=True)
    drought_index = models.FloatField(null=True, blank=True)
    moisture_stress_index = models.FloatField(null=True, blank=True)
    
    # Recommendations
    irrigation_recommended = models.BooleanField(default=False)
    irrigation_amount = models.FloatField(null=True, blank=True, help_text='Recommended irrigation in mm')
    protection_needed = models.BooleanField(default=False)
    protection_measures = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'crop_weather_indices'
        ordering = ['-date']
        unique_together = ['crop', 'location', 'date']
    
    def __str__(self):
        return f"{self.crop} - {self.location} - {self.date}"


class FarmerWeatherPreference(models.Model):
    """
    Model for storing farmer weather notification preferences
    """
    farmer = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weather_preferences'
    )
    location = models.CharField(max_length=255)
    
    # Notification preferences
    daily_forecast = models.BooleanField(default=True)
    weather_alerts = models.BooleanField(default=True)
    irrigation_reminders = models.BooleanField(default=True)
    
    # Thresholds
    rain_alert_threshold = models.FloatField(
        default=20, 
        help_text='Rainfall amount in mm to trigger alert'
    )
    temp_high_threshold = models.FloatField(
        default=40,
        help_text='High temperature threshold in Celsius'
    )
    temp_low_threshold = models.FloatField(
        default=10,
        help_text='Low temperature threshold in Celsius'
    )
    
    # Crops being monitored
    monitored_crops = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'farmer_weather_preferences'
    
    def __str__(self):
        return f"Weather Preferences - {self.farmer.name}"
