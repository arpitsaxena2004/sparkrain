from django.conf import settings
from django.db import models


class UserWaterSavings(models.Model):
    class Meta:
        db_table = "user_water_savings"
        ordering = ["-calculation_date"]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="water_savings",
    )
    session_key = models.CharField(max_length=40, blank=True, db_index=True)

    roof_area = models.FloatField()
    rainfall = models.FloatField()
    runoff_coefficient = models.FloatField(default=0.8)

    water_saved = models.FloatField(help_text="Liters per year")
    money_saved = models.FloatField(help_text="INR per year")
    badge = models.CharField(max_length=64)

    calculation_date = models.DateTimeField(auto_now_add=True)

class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    services_offered = models.TextField(help_text="Services this vendor provides.")
    description = models.TextField(blank=True, null=True)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class WaterTank(models.Model):
    """Water tank monitoring and management"""
    class Meta:
        db_table = "water_tank"
        ordering = ["-last_updated"]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="water_tanks",
    )
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    
    name = models.CharField(max_length=100, default="Main Tank")
    capacity_liters = models.FloatField(help_text="Total tank capacity in liters")
    current_level_liters = models.FloatField(help_text="Current water level in liters")
    location = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def level_percentage(self):
        """Calculate current fill percentage"""
        if self.capacity_liters <= 0:
            return 0
        return (self.current_level_liters / self.capacity_liters) * 100
    
    def __str__(self):
        return f"{self.name} - {self.level_percentage:.1f}%"


class FloodPredictionLog(models.Model):
    """Log of AI predictions for analysis and history"""
    class Meta:
        db_table = "flood_prediction_log"
        ordering = ["-prediction_time"]
    
    tank = models.ForeignKey(WaterTank, on_delete=models.CASCADE, related_name="predictions")
    
    risk_level = models.CharField(max_length=20)
    confidence = models.FloatField()
    predicted_rainfall_7days = models.FloatField()
    tank_level_pct = models.FloatField()
    recommended_action = models.TextField()
    system_action = models.TextField()
    alert_message = models.TextField()
    
    prediction_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.risk_level} - {self.prediction_time.strftime('%Y-%m-%d %H:%M')}"


class BorewellEstimation(models.Model):
    """Borewell depth estimation records"""
    class Meta:
        db_table = "borewell_estimation"
        ordering = ["-estimation_time"]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="borewell_estimations",
    )
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    
    location = models.CharField(max_length=200)
    annual_rainfall_mm = models.FloatField()
    region_type = models.CharField(max_length=20)
    soil_type = models.CharField(max_length=20)
    
    min_depth_feet = models.IntegerField()
    max_depth_feet = models.IntegerField()
    recommended_depth_feet = models.IntegerField()
    confidence_level = models.FloatField()
    water_availability = models.CharField(max_length=20)
    estimated_yield_lph = models.IntegerField()
    reasoning = models.TextField()
    cost_estimate_min = models.IntegerField()
    cost_estimate_max = models.IntegerField()
    
    estimation_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.location} - {self.recommended_depth_feet}ft - {self.estimation_time.strftime('%Y-%m-%d')}"
