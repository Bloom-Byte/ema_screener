from django.db import models
from rest_framework import generics, response, status
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from typing import Dict
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from currency.models import Currency
from currency.managers import CurrencyQuerySet
from currency.serializers import CurrencySerializer
from ema.models import EMARecord
from ema.serializers import EMARecordSerializer
from .filters import EMARecordQSFilterer
from .authentication import AuthTokenAuthentication


ema_record_qs = EMARecord.objects.select_related("currency").all()
currency_qs = Currency.objects.all()


@csrf_exempt
def health_check_api_view(request, *args, **kwargs) -> JsonResponse:
    """Simple view to test if the API server is up and running."""
    return JsonResponse(
        data={
            "message": "Server is !down."
        },
        status=status.HTTP_200_OK
    )


class UserAuthenticationAPIView(ObtainAuthToken):
    """API view for user authentication"""

    def post(self, request, *args, **kwargs) -> response.Response:
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return response.Response({
            'token': token.key,
            'user_id': user.pk,
        })



class UserLogoutAPIView(generics.GenericAPIView):
    """API view for user logout"""
    http_method_names = ["get"]

    def post(self, request, *args, **kwargs) -> response.Response:
        if request.user.is_authenticated:
            request.user.auth_token.delete()
        return response.Response(status=status.HTTP_200_OK)
    


class CurrencyListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating currencies"""
    model = Currency
    serializer_class = CurrencySerializer
    queryset = currency_qs
    url_search_param = "search"
    authentication_classes = [AuthTokenAuthentication]

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



class CurrencyDestroyAPIView(generics.DestroyAPIView):
    """API view for deleting a currency"""
    model = Currency
    queryset = currency_qs
    serializer_class = CurrencySerializer
    lookup_field = "id"
    lookup_url_kwarg = "currency_id"
    authentication_classes = [AuthTokenAuthentication]

        

class EMARecordListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating EMA records"""
    model = EMARecord
    serializer_class = EMARecordSerializer
    queryset = ema_record_qs

    def get_queryset(self) -> models.QuerySet[EMARecord]:
        ema_qs_filterer = EMARecordQSFilterer(self.request.query_params)
        ema_qs = super().get_queryset()
        return ema_qs_filterer.apply_filters(ema_qs)
    

    def get(self, request, *args, **kwargs) -> response.Response:
        """
        Retrieve a list of EMA records

        Tne following query parameters are supported:
        - timeframe: Duration of the timeframe in the format "HH:MM:SS" e.g. "1:00:00" for 1 hour
        - currency: Symbol or name of the currency
        - ema20: EMA20 value
        - ema50: EMA50 value
        - ema100: EMA100 value
        - ema200: EMA200 value
        - trend: Trend direction (1 for upwards, -1 for downwards, 0 for sideways)
        - watch: EMA watchlist type. Can be either be type "A", "B", or "C"
        """
        return super().get(request, *args, **kwargs)



user_authentication_api_view = csrf_exempt(UserAuthenticationAPIView.as_view())
user_logout_api_view = csrf_exempt(UserLogoutAPIView.as_view())
currency_list_create_api_view = csrf_exempt(CurrencyListCreateAPIView.as_view())
currency_destroy_api_view = csrf_exempt(CurrencyDestroyAPIView.as_view())
ema_record_list_create_api_view = csrf_exempt(EMARecordListCreateAPIView.as_view())
