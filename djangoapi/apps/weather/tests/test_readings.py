import uuid

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from ..models import WeatherReading

DATA_INFO = {
    'Temperature': 3.8,
    'TemperatureMax': 3.8,
    'TemperatureMin': 3.4,
    'Humidity': 89,
    'Rainfall': 0,
}


def _make_reading(**kwargs):
    defaults = {
        'sensor_name': 'aemet-zaorejas',
        'sensor_date': '2026-02-15T23:00:00+00:00',
        'data_info': DATA_INFO,
    }
    defaults.update(kwargs)
    return WeatherReading.objects.create(**defaults)


class WeatherReadingListGetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('weather:reading-list')

    def _get_data(self, params=None):
        return self.client.get(self.url, params or {}).json()

    def test_empty_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['results'], [])
        self.assertEqual(body['count'], 0)

    def test_returns_all_readings(self):
        _make_reading()
        _make_reading(sensor_date='2026-02-15T22:00:00+00:00')
        body = self._get_data()
        self.assertEqual(body['count'], 2)
        self.assertEqual(len(body['results']), 2)

    def test_filter_by_sensor_name_match(self):
        _make_reading(sensor_name='aemet-zaorejas')
        _make_reading(sensor_name='aemet-madrid')
        body = self._get_data({'sensorName': 'aemet-zaorejas'})
        self.assertEqual(body['count'], 1)
        self.assertEqual(body['results'][0]['sensorName'], 'aemet-zaorejas')

    def test_filter_by_sensor_name_no_match(self):
        _make_reading(sensor_name='aemet-zaorejas')
        body = self._get_data({'sensorName': 'aemet-unknown'})
        self.assertEqual(body['results'], [])
        self.assertEqual(body['count'], 0)

    def test_response_shape(self):
        reading = _make_reading()
        body = self._get_data()
        self.assertIn('count', body)
        self.assertIn('next', body)
        self.assertIn('previous', body)
        self.assertIn('results', body)
        item = body['results'][0]
        self.assertEqual(item['id'], str(reading.id))
        self.assertEqual(item['sensorName'], reading.sensor_name)
        self.assertIn('sensorDate', item)
        self.assertEqual(item['dataInfo'], DATA_INFO)

    def test_pagination_page_size(self):
        for i in range(5):
            _make_reading(sensor_date=f'2026-02-{10 + i:02d}T00:00:00+00:00')
        body = self._get_data({'pageSize': 2})
        self.assertEqual(body['count'], 5)
        self.assertEqual(len(body['results']), 2)
        self.assertIsNotNone(body['next'])

    def test_pagination_second_page(self):
        for i in range(4):
            _make_reading(sensor_date=f'2026-02-{10 + i:02d}T00:00:00+00:00')
        body = self._get_data({'pageSize': 2, 'page': 2})
        self.assertEqual(len(body['results']), 2)
        self.assertIsNotNone(body['previous'])
        self.assertIsNone(body['next'])

    def test_invalid_page_returns_404(self):
        # DRF PageNumberPagination raises NotFound for non-integer page
        response = self.client.get(self.url, {'page': 'abc'})
        self.assertEqual(response.status_code, 404)

    def test_invalid_page_size_uses_default(self):
        # DRF silently falls back to default page size for invalid pageSize
        _make_reading()
        response = self.client.get(self.url, {'pageSize': 'abc'})
        self.assertEqual(response.status_code, 200)


class WeatherReadingListPostTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('weather:reading-list')
        self.payload = {
            'sensorName': 'aemet-zaorejas',
            'sensorDate': '2026-02-15T23:00:00+00:00',
            'dataInfo': DATA_INFO,
        }

    def _post(self, payload):
        return self.client.post(self.url, data=payload, format='json')

    def test_create_reading_returns_201(self):
        response = self._post(self.payload)
        self.assertEqual(response.status_code, 201)

    def test_create_reading_persisted(self):
        self._post(self.payload)
        self.assertEqual(WeatherReading.objects.count(), 1)

    def test_create_reading_response_shape(self):
        data = self._post(self.payload).json()
        self.assertIn('id', data)
        self.assertEqual(data['sensorName'], 'aemet-zaorejas')
        self.assertEqual(data['dataInfo'], DATA_INFO)

    def test_create_reading_with_explicit_id(self):
        explicit_id = str(uuid.uuid4())
        data = self._post({**self.payload, 'id': explicit_id}).json()
        self.assertEqual(data['id'], explicit_id)

    def test_missing_sensor_name_returns_400(self):
        payload = {k: v for k, v in self.payload.items() if k != 'sensorName'}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('sensorName', response.json())

    def test_missing_sensor_date_returns_400(self):
        payload = {k: v for k, v in self.payload.items() if k != 'sensorDate'}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)

    def test_missing_data_info_returns_400(self):
        payload = {k: v for k, v in self.payload.items() if k != 'dataInfo'}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)

    def test_data_info_not_object_returns_400(self):
        response = self._post({**self.payload, 'dataInfo': 'not-an-object'})
        self.assertEqual(response.status_code, 400)

    def test_invalid_json_returns_400(self):
        response = self.client.post(self.url, data='not json', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_uuid_returns_400(self):
        response = self._post({**self.payload, 'id': 'not-a-uuid'})
        self.assertEqual(response.status_code, 400)


class WeatherReadingDetailGetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.reading = _make_reading()
        self.url = reverse('weather:reading-detail', kwargs={'pk': self.reading.id})

    def test_returns_200_for_existing(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_response_shape(self):
        data = self.client.get(self.url).json()
        self.assertEqual(data['id'], str(self.reading.id))
        self.assertEqual(data['sensorName'], self.reading.sensor_name)
        self.assertEqual(data['dataInfo'], DATA_INFO)

    def test_returns_404_for_unknown_id(self):
        url = reverse('weather:reading-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
