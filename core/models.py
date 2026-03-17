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
