from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path('ws/ema-records/', consumers.ema_records_events_consumer),
]
