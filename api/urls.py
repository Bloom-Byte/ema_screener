from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

app_name = "api-v1"

urlpatterns = [
    path("", csrf_exempt(views.health_check_api_view), name="api-health-check"),
    path("ema-records/", csrf_exempt(views.ema_record_list_create_api_view), name="ema-record__list-create"),
]
