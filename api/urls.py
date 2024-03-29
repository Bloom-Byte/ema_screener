from django.urls import path

from . import views

app_name = "api-v1"

urlpatterns = [
    path("ema-record/", views.ema_record_list_create_api_view, name="ema-record__list-create"),
]
