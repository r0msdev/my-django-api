from django.urls import include, path

urlpatterns = [
    path('weather/', include('apps.weather.api.urls')),
]
