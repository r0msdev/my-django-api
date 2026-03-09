"""Production settings."""

import environ

from .base import *  # noqa: F401, F403  # pylint: disable=wildcard-import,unused-wildcard-import

env = environ.Env()

# SECRET_KEY must be set via environment — no fallback in prod
if not env('DJANGO_SECRET_KEY', default=None):
    raise RuntimeError('DJANGO_SECRET_KEY environment variable is not set.')

DEBUG = False

# Security hardening
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
