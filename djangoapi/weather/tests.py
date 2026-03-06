import json
import uuid

from django.test import Client, TestCase
from django.urls import reverse

from .models import WeatherReading

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


class WeatherReadingListGetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('weather:reading-list')

    def test_empty_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [])

    def test_returns_all_readings(self):
        _make_reading()
        _make_reading(sensor_date='2026-02-15T22:00:00+00:00')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), 2)

    def test_filter_by_sensor_name_match(self):
        _make_reading(sensor_name='aemet-zaorejas')
        _make_reading(sensor_name='aemet-madrid')
        response = self.client.get(self.url, {'sensorName': 'aemet-zaorejas'})
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['sensorName'], 'aemet-zaorejas')

    def test_filter_by_sensor_name_no_match(self):
        _make_reading(sensor_name='aemet-zaorejas')
        response = self.client.get(self.url, {'sensorName': 'aemet-unknown'})
        self.assertEqual(json.loads(response.content), [])

    def test_response_shape(self):
        reading = _make_reading()
        data = json.loads(self.client.get(self.url).content)[0]
        self.assertEqual(data['id'], str(reading.id))
        self.assertEqual(data['sensorName'], reading.sensor_name)
        self.assertIn('sensorDate', data)
        self.assertEqual(data['dataInfo'], DATA_INFO)


class WeatherReadingListPostTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('weather:reading-list')
        self.payload = {
            'sensorName': 'aemet-zaorejas',
            'sensorDate': '2026-02-15T23:00:00+00:00',
            'dataInfo': DATA_INFO,
        }

    def _post(self, payload):
        return self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json',
        )

    def test_create_reading_returns_201(self):
        response = self._post(self.payload)
        self.assertEqual(response.status_code, 201)

    def test_create_reading_persisted(self):
        self._post(self.payload)
        self.assertEqual(WeatherReading.objects.count(), 1)

    def test_create_reading_response_shape(self):
        data = json.loads(self._post(self.payload).content)
        self.assertIn('id', data)
        self.assertEqual(data['sensorName'], 'aemet-zaorejas')
        self.assertEqual(data['dataInfo'], DATA_INFO)

    def test_create_reading_with_explicit_id(self):
        explicit_id = str(uuid.uuid4())
        payload = {**self.payload, 'id': explicit_id}
        data = json.loads(self._post(payload).content)
        self.assertEqual(data['id'], explicit_id)

    def test_missing_sensor_name_returns_400(self):
        payload = {k: v for k, v in self.payload.items() if k != 'sensorName'}
        response = self._post(payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('sensorName', json.loads(response.content)['error'])

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


class WeatherReadingDetailGetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.reading = _make_reading()
        self.url = reverse('weather:reading-detail', kwargs={'pk': self.reading.id})

    def test_returns_200_for_existing(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_response_shape(self):
        data = json.loads(self.client.get(self.url).content)
        self.assertEqual(data['id'], str(self.reading.id))
        self.assertEqual(data['sensorName'], self.reading.sensor_name)
        self.assertEqual(data['dataInfo'], DATA_INFO)

    def test_returns_404_for_unknown_id(self):
        url = reverse('weather:reading-detail', kwargs={'pk': uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

