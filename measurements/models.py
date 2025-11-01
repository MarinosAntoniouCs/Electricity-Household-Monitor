from django.db import models
from django.core.validators import MinValueValidator


class Measurement(models.Model):
    meter_id = models.CharField(max_length=100, default='APARTMENT_METER')
    timestamp = models.DateTimeField(help_text="Start time of measurement")
    consumption_kwh = models.DecimalField(max_digits=10, decimal_places=4)
    cost = models.DecimalField(max_digits=10, decimal_places=4)
    cost_per_kwh = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    
    # NEW: End time field
    end_timestamp = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="End time of measurement period"
    )
    
    # Existing fields
    consumption_kwh = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        validators=[MinValueValidator(0)]
    )
    cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    
    # NEW: Calculated fields
    duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duration of measurement period in minutes"
    )
    
    average_power_kw = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Average power during period (kW)"
    )
    
    cost_per_kwh = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Cost per kilowatt-hour ($/kWh)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically calculate the rate
        if self.consumption_kwh and self.cost and self.consumption_kwh > 0:
            self.cost_per_kwh = self.cost / self.consumption_kwh
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['meter_id', 'timestamp']
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['meter_id', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Meter {self.meter_id} - {self.timestamp} - {self.consumption_kwh} kWh"