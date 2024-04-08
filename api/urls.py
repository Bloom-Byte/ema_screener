from django.urls import path

from . import views

app_name = "api-v1"

urlpatterns = [
    path("", views.health_check_api_view, name="api-health-check"),

    # Authentication
    path("accounts/auth/", views.user_authentication_api_view, name="account__auth"),
    path("accounts/logout/", views.user_logout_api_view, name="account__logout"),
    path("accounts/request-password-reset/", views.password_reset_request_api_view, name="account__password-reset-request"),
    path("accounts/validate-reset-token/", views.check_reset_token_validity_api_view, name="account__validate-reset-token"),
    path("accounts/reset-password/", views.password_reset_api_view, name="account__reset-password"),

    # Currencies
    path("currencies/", views.currency_list_create_api_view, name="currency__list-create"),
    path("currencies/<uuid:currency_id>/delete/", views.currency_destroy_api_view, name="currency__delete"),

    # EMA Records
    path("ema-records/", views.ema_record_list_create_api_view, name="ema-record__list-create"),
]
