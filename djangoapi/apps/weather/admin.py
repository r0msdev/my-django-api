from django.contrib import admin

from .domain.models import WeatherReading


@admin.register(WeatherReading)
class WeatherReadingAdmin(admin.ModelAdmin):
    list_display = ('id', 'sensor_name', 'sensor_date')
    list_filter = ('sensor_name',)
    ordering = ('-sensor_date',)
    list_per_page = 20
