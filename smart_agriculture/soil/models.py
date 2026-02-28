"""
Soil App Models
"""
from django.db import models
from django.conf import settings


class SoilData(models.Model):
    """
    Model for storing soil test data
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='soil_tests'
    )
    test_date = models.DateField()
    location = models.CharField(max_length=255)
    
    # Macronutrients
    nitrogen = models.FloatField(help_text='Nitrogen content in kg/ha')
    phosphorus = models.FloatField(help_text='Phosphorus content in kg/ha')
    potassium = models.FloatField(help_text='Potassium content in kg/ha')
    
    # pH and other parameters
    ph_level = models.FloatField(help_text='pH level')
    organic_carbon = models.FloatField(null=True, blank=True, help_text='Organic carbon %')
    electrical_conductivity = models.FloatField(null=True, blank=True, help_text='EC in dS/m')
    
    # Micronutrients (optional)
    zinc = models.FloatField(null=True, blank=True, help_text='Zinc in ppm')
    iron = models.FloatField(null=True, blank=True, help_text='Iron in ppm')
    manganese = models.FloatField(null=True, blank=True, help_text='Manganese in ppm')
    copper = models.FloatField(null=True, blank=True, help_text='Copper in ppm')
    boron = models.FloatField(null=True, blank=True, help_text='Boron in ppm')
    
    # Soil physical properties
    soil_texture = models.CharField(
        max_length=50,
        choices=[
            ('sandy', 'Sandy'),
            ('loamy', 'Loamy'),
            ('clay', 'Clay'),
            ('silty', 'Silty'),
            ('sandy_loam', 'Sandy Loam'),
            ('clay_loam', 'Clay Loam'),
            ('silty_loam', 'Silty Loam'),
        ],
        blank=True,
        null=True
    )
    soil_color = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'soil_data'
        ordering = ['-test_date']
    
    def __str__(self):
        return f"Soil Test - {self.location} - {self.test_date}"
    
    @property
    def npk_ratio(self):
        """Calculate NPK ratio"""
        if self.phosphorus == 0:
            return "N/A"
        n_ratio = round(self.nitrogen / self.phosphorus, 1)
        k_ratio = round(self.potassium / self.phosphorus, 1)
        return f"{n_ratio}:{1}:{k_ratio}"


class SoilTestReport(models.Model):
    """
    Model for storing soil test reports
    """
    soil_data = models.OneToOneField(
        SoilData,
        on_delete=models.CASCADE,
        related_name='report'
    )
    report_file = models.FileField(upload_to='soil_reports/')
    recommendations = models.TextField()
    suitable_crops = models.JSONField(default=list)
    fertility_rating = models.CharField(
        max_length=20,
        choices=[
            ('very_low', 'Very Low'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('very_high', 'Very High'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'soil_test_reports'
    
    def __str__(self):
        return f"Report - {self.soil_data.location}"


class FertilizerApplication(models.Model):
    """
    Model for tracking fertilizer applications
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fertilizer_applications'
    )
    crop = models.CharField(max_length=100)
    field_location = models.CharField(max_length=255)
    application_date = models.DateField()
    
    # Fertilizer details
    fertilizer_name = models.CharField(max_length=200)
    fertilizer_type = models.CharField(
        max_length=50,
        choices=[
            ('organic', 'Organic'),
            ('inorganic', 'Inorganic/Chemical'),
            ('bio', 'Bio-fertilizer'),
            ('micronutrient', 'Micronutrient'),
        ]
    )
    quantity_applied = models.FloatField(help_text='Quantity in kg')
    application_method = models.CharField(
        max_length=50,
        choices=[
            ('broadcasting', 'Broadcasting'),
            ('banding', 'Banding'),
            ('foliar', 'Foliar Spray'),
            ('fertigation', 'Fertigation'),
            ('top_dressing', 'Top Dressing'),
        ]
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Results
    effectiveness_rating = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fertilizer_applications'
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.fertilizer_name} - {self.crop} - {self.application_date}"
