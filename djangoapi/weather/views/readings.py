import json
import logging
import uuid

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.errors import error_response
from core.pagination import paginate_queryset, parse_pagination

from ..models import WeatherReading

logger = logging.getLogger('weather')


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
        return None, error_response('Invalid JSON body.')


@method_decorator(csrf_exempt, name='dispatch')
class WeatherReadingListView(View):
    """GET /weather/  – list all readings (paginated).
    POST /weather/ – create a new reading."""

    def get(self, request):
        page, page_size, err = parse_pagination(request)
        if err:
            return err

        readings = WeatherReading.objects.all()
        sensor_name = request.GET.get('sensorName')
        if sensor_name:
            readings = readings.filter(sensor_name=sensor_name)
            logger.debug('Filtering readings by sensorName=%s', sensor_name)

        items, meta = paginate_queryset(readings, page, page_size)
        logger.debug('GET readings list — page=%s page_size=%s total=%s', page, page_size, meta['total'])
        return JsonResponse({'meta': meta, 'data': [_reading_to_dict(r) for r in items]})

    def post(self, request):
        body, err = _parse_body(request)
        if err:
            return err

        required = {'sensorName', 'sensorDate', 'dataInfo'}
        missing = required - set(body.keys())
        if missing:
            return error_response(f'Missing required fields: {", ".join(sorted(missing))}.')

        if not isinstance(body['dataInfo'], dict):
            return error_response('dataInfo must be a JSON object.')

        reading = WeatherReading(
            sensor_name=body['sensorName'],
            sensor_date=body['sensorDate'],
            data_info=body['dataInfo'],
        )

        if 'id' in body:
            try:
                reading.id = uuid.UUID(str(body['id']))
            except (ValueError, AttributeError):
                return error_response('id must be a valid UUID.')

        try:
            reading.full_clean()
        except ValidationError as exc:
            return error_response(exc.message_dict)

        reading.save()
        logger.info('Created WeatherReading id=%s sensor=%s', reading.id, reading.sensor_name)
        return JsonResponse(_reading_to_dict(reading), status=201)


@method_decorator(csrf_exempt, name='dispatch')
class WeatherReadingDetailView(View):
    """GET /weather/<uuid>/ – retrieve a single reading."""

    def get(self, request, pk):
        try:
            reading = WeatherReading.objects.get(pk=pk)
        except WeatherReading.DoesNotExist:
            logger.warning('WeatherReading not found: pk=%s', pk)
            return error_response('Not found.', status=404)

        return JsonResponse(_reading_to_dict(reading))
