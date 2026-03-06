"""Development settings — never use in production."""

from .base import *  # noqa: F401, F403

SECRET_KEY = 'django-insecure-^cu^g41$5euelcb(27bi(lseo#kbaw8yf8ruw$#dtuk_++1=j^'

DEBUG = True

ALLOWED_HOSTS = ['*']

# More verbose logging in dev
LOGGING['loggers']['weather']['level'] = 'DEBUG'   # noqa: F405
LOGGING['loggers']['core']['level'] = 'DEBUG'      # noqa: F405
