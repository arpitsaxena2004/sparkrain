from django.contrib import admin

from .models import Vendor, UserWaterSavings, WaterTank, FloodPredictionLog, BorewellEstimation

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'contact_email', 'phone_number', 'added_date')
    search_fields = ('name', 'services_offered', 'address')
    list_filter = ('added_date',)


@admin.register(UserWaterSavings)
class UserWaterSavingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'roof_area', 'rainfall', 'water_saved', 'badge', 'calculation_date')
    list_filter = ('badge', 'calculation_date')
    search_fields = ('user__username', 'session_key')
    readonly_fields = ('calculation_date',)


@admin.register(WaterTank)
class WaterTankAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'capacity_liters', 'level_percentage_display', 'location', 'last_updated')
    list_filter = ('last_updated', 'created_at')
    search_fields = ('name', 'location', 'user__username')
    readonly_fields = ('last_updated', 'created_at')
    
    def level_percentage_display(self, obj):
        return f"{obj.level_percentage:.1f}%"
    level_percentage_display.short_description = 'Current Level'


@admin.register(FloodPredictionLog)
class FloodPredictionLogAdmin(admin.ModelAdmin):
    list_display = ('tank', 'risk_level', 'confidence', 'predicted_rainfall_7days', 'tank_level_pct', 'prediction_time')
    list_filter = ('risk_level', 'prediction_time')
    search_fields = ('tank__name', 'alert_message')
    readonly_fields = ('prediction_time',)
    date_hierarchy = 'prediction_time'


@admin.register(BorewellEstimation)
class BorewellEstimationAdmin(admin.ModelAdmin):
    list_display = ('location', 'recommended_depth_feet', 'water_availability', 'confidence_level', 'estimation_time')
    list_filter = ('water_availability', 'region_type', 'soil_type', 'estimation_time')
    search_fields = ('location', 'user__username')
    readonly_fields = ('estimation_time',)
    date_hierarchy = 'estimation_time'
