import logging

from rest_framework.generics import ListCreateAPIView, RetrieveAPIView

from apps.weather.api.serializers import WeatherReadingSerializer
from apps.weather.services import readings as service

logger = logging.getLogger('weather')


class WeatherReadingListView(ListCreateAPIView):
    """GET /weather/readings/  – list all readings (paginated).
    POST /weather/readings/ – create a new reading."""

    serializer_class = WeatherReadingSerializer

    def get_queryset(self):
        sensor_name = self.request.query_params.get('sensorName')
        return service.get_readings_list(sensor_name=sensor_name)

    def perform_create(self, serializer):
        reading = service.create_reading(serializer.validated_data)
        serializer.instance = reading


class WeatherReadingDetailView(RetrieveAPIView):
    """GET /weather/readings/<uuid>/ – retrieve a single reading."""

    serializer_class = WeatherReadingSerializer

    def get_queryset(self):
        return service.get_readings_list()
