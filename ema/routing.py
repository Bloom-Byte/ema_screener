from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path('ws/ema-records/update/', consumers.ema_record_update_consumer),
]
