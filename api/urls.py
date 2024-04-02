from django.urls import path

from . import views

app_name = "api-v1"

urlpatterns = [
    path("", views.health_check_api_view, name="api-health-check"),

    # Authentication
    path("auth/", views.user_authentication_api_view, name="user-auth"),
    path("logout/", views.user_logout_api_view, name="user-logout"),

    # Currencies
    path("currencies/", views.currency_list_create_api_view, name="currency__list-create"),
    path("currencies/<uuid:currency_id>/delete", views.currency_destroy_api_view, name="currency-delete"),

    # EMA Records
    path("ema-records/", views.ema_record_list_create_api_view, name="ema-record__list-create"),
]
