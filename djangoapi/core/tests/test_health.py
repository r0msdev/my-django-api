from unittest.mock import patch

from django.db import OperationalError
from django.test import TestCase
from django.urls import reverse


class HealthViewTests(TestCase):

    def test_returns_200_when_db_ok(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)

    def test_response_shape_when_db_ok(self):
        response = self.client.get(reverse('health'))
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['db'], 'ok')

    def test_returns_503_when_db_unreachable(self):
        with patch('core.views.connection.ensure_connection', side_effect=OperationalError):
            response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 503)

    def test_response_shape_when_db_unreachable(self):
        with patch('core.views.connection.ensure_connection', side_effect=OperationalError):
            response = self.client.get(reverse('health'))
        data = response.json()
        self.assertEqual(data['status'], 'degraded')
        self.assertEqual(data['db'], 'error')
