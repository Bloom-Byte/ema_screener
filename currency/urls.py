from django.urls import path

from . import views

app_name = "currencies"


urlpatterns = [
    path("", views.currency_list_create_api_view, name="currency__list-create"),
    path("categories/", views.currency_category_list_api_view, name="currency-category__list"),
    path("<uuid:currency_id>/delete/", views.currency_destroy_api_view, name="currency__delete"),
]
