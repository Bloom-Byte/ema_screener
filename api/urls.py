from django.urls import include, path

from . import views

app_name = "api"


urlpatterns = [
    path("", views.health_check_api_view, name="api-health-check"),
    path("accounts/", include("users.urls", namespace="users")),
    path("currencies/", include("currency.urls", namespace="currencies")),
    path("ema-records/", include('ema.urls', namespace="ema_records")),
]
