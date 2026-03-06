import logging

from django.http import JsonResponse

logger = logging.getLogger('core')


def error_response(message, status=400):
    """Return a consistently shaped JSON error response."""
    return JsonResponse({'error': message}, status=status)


# ── Global error handlers (wired in app/urls.py) ─────────────────────────────

def handler400(request, exception=None):
    logger.warning('400 Bad Request: %s', request.path)
    return error_response('Bad request.', status=400)


def handler403(request, exception=None):
    logger.warning('403 Forbidden: %s', request.path)
    return error_response('Forbidden.', status=403)


def handler404(request, exception=None):
    logger.warning('404 Not Found: %s', request.path)
    return error_response('Not found.', status=404)


def handler500(request):
    logger.error('500 Internal Server Error: %s', request.path)
    return error_response('Internal server error.', status=500)
