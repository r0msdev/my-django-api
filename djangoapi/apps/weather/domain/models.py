import uuid

from django.db import models


class WeatherReading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sensor_name = models.CharField(max_length=255)
    sensor_date = models.DateTimeField()
    data_info = models.JSONField()

    class Meta:
        ordering = ['-sensor_date']
        app_label = 'weather'

    def __str__(self):
        return f"{self.sensor_name} @ {self.sensor_date}"
