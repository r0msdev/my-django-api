import json
import uuid

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import WeatherReading


def _reading_to_dict(reading):
    return {
        'id': str(reading.id),
        'sensorName': reading.sensor_name,
        'sensorDate': reading.sensor_date.isoformat(),
        'dataInfo': reading.data_info,
    }


def _parse_body(request):
    """Return (data, error_response). One of them is always None."""
    try:
        return json.loads(request.body), None
    except json.JSONDecodeError:
        return None, JsonResponse({'error': 'Invalid JSON body.'}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class WeatherReadingListView(View):
    """GET /weather/  – list all readings.
    POST /weather/ – create a new reading."""

    def get(self, request):
        readings = WeatherReading.objects.all()
        sensor_name = request.GET.get('sensorName')
        if sensor_name:
            readings = readings.filter(sensor_name=sensor_name)
        return JsonResponse([_reading_to_dict(r) for r in readings], safe=False)

    def post(self, request):
        body, err = _parse_body(request)
        if err:
            return err

        required = {'sensorName', 'sensorDate', 'dataInfo'}
        missing = required - set(body.keys())
        if missing:
            return JsonResponse(
                {'error': f'Missing required fields: {", ".join(sorted(missing))}.'},
                status=400,
            )

        if not isinstance(body['dataInfo'], dict):
            return JsonResponse({'error': 'dataInfo must be a JSON object.'}, status=400)

        reading = WeatherReading(
            sensor_name=body['sensorName'],
            sensor_date=body['sensorDate'],
            data_info=body['dataInfo'],
        )

        if 'id' in body:
            try:
                reading.id = uuid.UUID(str(body['id']))
            except (ValueError, AttributeError):
                return JsonResponse({'error': 'id must be a valid UUID.'}, status=400)

        try:
            reading.full_clean()
        except ValidationError as exc:
            return JsonResponse({'error': exc.message_dict}, status=400)

        reading.save()
        return JsonResponse(_reading_to_dict(reading), status=201)


@method_decorator(csrf_exempt, name='dispatch')
class WeatherReadingDetailView(View):
    """GET /weather/<uuid>/ – retrieve a single reading."""

    def get(self, request, pk):
        try:
            reading = WeatherReading.objects.get(pk=pk)
        except WeatherReading.DoesNotExist:
            return JsonResponse({'error': 'Not found.'}, status=404)

        return JsonResponse(_reading_to_dict(reading))
