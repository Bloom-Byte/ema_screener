
from django.http import Http404
from rest_framework import generics, response, status, views
from django.views.decorators.csrf import csrf_exempt
from typing import Dict


from currency.models import Currency
from currency.managers import CurrencyQuerySet
from currency.serializers import CurrencySerializer
from api.permission_mixins import AuthenticationRequired, AuthenticationRequiredOrReadOnly

from helpers.logging import log_exception


currency_qs = Currency.objects.all()



class CurrencyListCreateAPIView(AuthenticationRequiredOrReadOnly, generics.ListCreateAPIView):
    """API view for listing and creating currencies"""
    model = Currency
    serializer_class = CurrencySerializer
    queryset = currency_qs
    url_search_param = "search"

    def get_queryset(self) -> CurrencyQuerySet[Currency]:
        currency_qs = super().get_queryset()
        query_params: Dict = self.request.query_params
        search_query = query_params.get(self.url_search_param, None)
        if search_query:
            currency_qs = currency_qs.search(query=search_query)
        return currency_qs

    
    def get(self, request, *args, **kwargs) -> response.Response:
        """
        Retrieve a list of currencies

        The following query parameters are supported:
        - search: Search query to filter currencies by name, symbol, category, or subcategory
        """
        return super().get(request, *args, **kwargs)
    



class CurrencyCategoryListAPIView(views.APIView):
    """API view for listing currency categories and subcategories"""
    queryset = currency_qs
    http_method_names = ["get"]
    
    def get(self, request, *args, **kwargs) -> response.Response:
        """
        Retrieve a list of currency categories
        """
        currencies = self.queryset
        categories = currencies.values_list("category", flat=True).distinct()
        subcategories = currencies.values_list("subcategory", flat=True).distinct()
        return response.Response(
            data={
                "status": "success",
                "message": "Currency categories retrieved successfully!",
                "data": {
                    "categories": set(categories),
                    "subcategories": set(subcategories)
                }
            },
            status=status.HTTP_200_OK
        )




class CurrencyDestroyAPIView(AuthenticationRequired, generics.DestroyAPIView):
    """API view for deleting a currency"""
    model = Currency
    queryset = currency_qs
    lookup_field = "id"
    lookup_url_kwarg = "currency_id"
    
    def delete(self, request, *args, **kwargs) -> response.Response:
        try:
            currency = self.get_object()
            currency.delete()
        except Http404 as exc:
            # Catch the Http404 exception and return a structured response
            return response.Response(
                data={
                    "status": "error",
                    "message": str(exc)
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as exc:
            log_exception(exc)
            return response.Response(
                data={
                    "status": "error",
                    "message": "An error occurred while attempting to delete the currency!"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return response.Response(
            data={
                "status": "success",
                "message": f"{currency} was deleted successfully!"
            },
            status=status.HTTP_200_OK
        )

        

currency_list_create_api_view = csrf_exempt(CurrencyListCreateAPIView.as_view())
currency_category_list_api_view = csrf_exempt(CurrencyCategoryListAPIView.as_view())
currency_destroy_api_view = csrf_exempt(CurrencyDestroyAPIView.as_view())
