from django.urls import path

from . import views

app_name = "users"


urlpatterns = [
    path("auth/", views.user_authentication_api_view, name="account__auth"),
    path("logout/", views.user_logout_api_view, name="account__logout"),
    path("request-password-reset/", views.password_reset_request_api_view, name="account__password-reset-request"),
    path("validate-reset-token/", views.check_reset_token_validity_api_view, name="account__validate-reset-token"),
    path("reset-password/", views.password_reset_api_view, name="account__reset-password"),
]
