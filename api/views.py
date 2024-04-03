from django.db import models
from django.http import JsonResponse
from rest_framework import generics, response, status, views
from django.views.decorators.csrf import csrf_exempt
from typing import Dict
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


from currency.models import Currency
from currency.managers import CurrencyQuerySet
from currency.serializers import CurrencySerializer
from distutils.command import check
from ema.models import EMARecord
from ema.serializers import EMARecordSerializer
from .filters import EMARecordQSFilterer
from .serializers import UserIDSerializer
from users.password_reset import (
    send_password_reset_mail, check_if_password_reset_token_exists, create_password_reset_token
)
from helpers.logging import log_exception


UserModel = get_user_model()
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
        return response.Response(
            data={
                "status": "success",
                "message": f"{user} was authenticated successfully",
                "data":{
                    'token': token.key,
                    'user_id': user.pk,
                }
            },
            status=status.HTTP_200_OK
        )



class UserLogoutAPIView(views.APIView):
    """
    API view for logging out a user. 

    This should be used when a user wants to logout of all devices.
    """
    http_method_names = ["post"]
    serializer_class = UserIDSerializer

    def post(self, request, *args, **kwargs) -> response.Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data.get("user_id")
        
        try:
            user = UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return response.Response(
                data={
                    "status": "error",
                    "message": "User with the given ID does not exist!"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            user.auth_token.delete()
        except Exception:
            # User does not have an auth token and was not authenticated
            return response.Response(
                data={
                    "status": "error",
                    "message": "Only authenticated users can be logged out!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return response.Response(
            data={
                "status": "success",
                "message": f"{user} was logged out successfully!"
            },
            status=status.HTTP_200_OK
        )



class PasswordResetRequestAPIView(views.APIView):
    """
    API view for requesting a password reset.

    An email will be sent to the user with a link to reset their password.
    """
    http_method_names = ["post"]
    serializer_class = UserIDSerializer

    def post(self, request, *args, **kwargs) -> response.Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.validated_data.get("user_id")

        if request.user.id != user_id:
            return response.Response(
                data={
                    "status": "error",
                    "message": "You are not authorized to perform this action!"
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        if check_if_password_reset_token_exists(request.user):
            # If a token already exists, then the user has already requested a password reset
            # and should wait for the email to be sent to them or check their email for the link.
            return response.Response(
                data={
                    "status": "error",
                    "message": "A password reset request has already been made for this account!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = None  
        try:
            # Create a token that is valid for 24 hours
            token = create_password_reset_token(request.user, validity_period_in_hours=24)
            send_password_reset_mail(request.user, request, token)
        except Exception as exc:
            log_exception(exc)
            # Delete the token if an error occurs
            if token:
                token.delete()
            return response.Response(
                data={
                    "status": "error",
                    "message": "An error occurred while processing your request!"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return response.Response(
            data={
                "status": "success",
                "message": f"Request processed successfully. An email has been sent to {request.user.email}."
            },
            status=status.HTTP_200_OK
        )



class PasswordResetAPIView(views.APIView):
    """API view for resetting user account password"""
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs) -> response.Response:
        pass



class CurrencyListCreateAPIView(generics.ListCreateAPIView):
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



class CurrencyDestroyAPIView(generics.DestroyAPIView):
    """API view for deleting a currency"""
    model = Currency
    queryset = currency_qs
    serializer_class = CurrencySerializer
    lookup_field = "id"
    lookup_url_kwarg = "currency_id"

        

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



# User Authentication API Views
user_authentication_api_view = csrf_exempt(UserAuthenticationAPIView.as_view())
user_logout_api_view = csrf_exempt(UserLogoutAPIView.as_view())
password_reset_request_api_view = csrf_exempt(PasswordResetRequestAPIView.as_view())
password_reset_api_view = csrf_exempt(PasswordResetAPIView.as_view())

# Model API Views
currency_list_create_api_view = csrf_exempt(CurrencyListCreateAPIView.as_view())
currency_destroy_api_view = csrf_exempt(CurrencyDestroyAPIView.as_view())
ema_record_list_create_api_view = csrf_exempt(EMARecordListCreateAPIView.as_view())
