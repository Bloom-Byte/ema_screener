from django.urls import path

from . import views


app_name = "ema_records"

urlpatterns = [
    path("", views.ema_record_list_create_api_view, name="ema-record__list-create"),
]

