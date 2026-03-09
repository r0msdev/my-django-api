from django.urls import path

from core.views import health, index

urlpatterns = [
    path('', index, name='index'),
    path('health/', health, name='health'),
]
