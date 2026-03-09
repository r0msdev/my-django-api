from apps.weather.domain.models import WeatherReading


def list_readings(sensor_name=None):
    """Return all readings queryset, optionally filtered by sensor name."""
    qs = WeatherReading.objects.all()
    if sensor_name:
        qs = qs.filter(sensor_name=sensor_name)
    return qs


def create_reading(validated_data):
    """Persist a new WeatherReading from validated serializer data."""
    return WeatherReading.objects.create(**validated_data)
