from django.contrib import admin
from .models import Measurement


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = [
        'meter_id', 
        'timestamp', 
        'end_timestamp',
        'consumption_kwh', 
        'cost',
        'duration_minutes',
        'average_power_kw',
        'cost_per_kwh',
        'created_at'
    ]
    list_filter = ['meter_id', 'timestamp']
    search_fields = ['meter_id']
    readonly_fields = ['created_at', 'updated_at', 'duration_minutes', 'average_power_kw', 'cost_per_kwh']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('meter_id', 'timestamp', 'end_timestamp', 'consumption_kwh', 'cost')
        }),
        ('Calculated Metrics', {
            'fields': ('duration_minutes', 'average_power_kw', 'cost_per_kwh'),
            'classes': ('collapse',)
        }),
        ('Optional Electrical Measurements', {
            'fields': ('voltage', 'current', 'power_factor'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )