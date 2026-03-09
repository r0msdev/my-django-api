from django.urls import path

from core.health import health, index

urlpatterns = [
    path('', index, name='index'),
    path('health/', health, name='health'),
]
