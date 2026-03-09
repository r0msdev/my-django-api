from django.urls import path

from .views import WeatherReadingDetailView, WeatherReadingListView

app_name = 'weather'

urlpatterns = [
    path('', WeatherReadingListView.as_view(), name='reading-list'),
    path('<uuid:pk>/', WeatherReadingDetailView.as_view(), name='reading-detail'),
]
