import logging

from django.db import OperationalError, connection
from django.http import JsonResponse

logger = logging.getLogger('core')


def index(request):
    """Root endpoint — returns available API routes."""
    return JsonResponse({
        'endpoints': {
            'health': '/health/',
            'weather': '/api/v1/weather/readings/',
        }
    })


def health(request):
    """Return service liveness and basic dependency status."""
    try:
        connection.ensure_connection()
        db_status = 'ok'
    except OperationalError:
        db_status = 'error'
        logger.error('Health check: database unreachable')

    status = 200 if db_status == 'ok' else 503
    return JsonResponse(
        {'status': 'ok' if status == 200 else 'degraded', 'db': db_status},
        status=status,
    )
