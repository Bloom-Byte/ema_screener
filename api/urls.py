from django.urls import path

from . import views

app_name = "api-v1"

urlpatterns = [
    path("", views.health_check_api_view, name="api-health-check"),
    path("ema-records/", views.ema_record_list_create_api_view, name="ema-record__list-create"),
]
