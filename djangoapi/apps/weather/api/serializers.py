import uuid

from rest_framework import serializers

from apps.weather.domain.models import WeatherReading


class WeatherReadingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False, default=uuid.uuid4)
    sensorName = serializers.CharField(source='sensor_name')
    sensorDate = serializers.DateTimeField(source='sensor_date')
    dataInfo = serializers.JSONField(source='data_info')

    class Meta:
        model = WeatherReading
        fields = ['id', 'sensorName', 'sensorDate', 'dataInfo']

    def validate_dataInfo(self, value):  # pylint: disable=invalid-name
        if not isinstance(value, dict):
            raise serializers.ValidationError('dataInfo must be a JSON object.')
        return value
