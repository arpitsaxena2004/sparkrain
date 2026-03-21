from django.contrib import admin

from .models import Vendor, UserWaterSavings

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'contact_email', 'phone_number', 'added_date')
    search_fields = ('name', 'services_offered', 'address')
    list_filter = ('added_date',)

# Register your models here.
