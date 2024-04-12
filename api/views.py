from django.db import models
from django.http import JsonResponse, Http404
from rest_framework import generics, response, status, views
from django.views.decorators.csrf import csrf_exempt
from typing import Dict
from django.contrib.auth import get_user_model
from django.conf import settings

from currency.models import Currency
from currency.managers import CurrencyQuerySet
from currency.serializers import CurrencySerializer
from ema.models import EMARecord
from ema.serializers import EMARecordSerializer
from .filters import EMARecordQSFilterer
from .authentication import universal_logout
from .permissions import HasAPIKeyOrIsAuthenticated
from tokens.views import AuthTokenAuthenticationAPIView
from users.serializers import (
    UserIDSerializer, PasswordResetRequestSerializer, 
    PasswordResetSerializer, PasswordResetTokenSerializer
)
from users.password_reset import (
    check_if_password_reset_token_exists, check_password_reset_token_validity,
    create_password_reset_token, construct_password_reset_mail, 
    delete_password_reset_token, reset_password_for_token, get_token_owner
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



class UserAuthenticationAPIView(AuthTokenAuthenticationAPIView):
    """API view for user authentication"""

    def get_response_data(self, user, token) -> Dict:
        return {
            "status": "success",
            "message": f"{user} was authenticated successfully",
            "data": {
                'token': token.key,
                'user_id': user.pk,
            }
        }
    

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

        logged_out = universal_logout(request.user)
        if not logged_out:
            return response.Response(
                data={
                    "status": "error",
                    "message": "User could not be logged out! You are probably already logged out."
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
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (HasAPIKeyOrIsAuthenticated,)

    def post(self, request, *args, **kwargs) -> response.Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email")
        token_name = serializer.validated_data.get("token_name")
        token = None

        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return response.Response(
                data={
                    "status": "error",
                    "message": f"User account with email address {email}, not found!"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        if check_if_password_reset_token_exists(user) is True:
            # If a token already exists, then the user has already requested a password reset
            # and should wait for the email to be sent to them or check their email for the link.
            return response.Response(
                data={
                    "status": "error",
                    "message": f"A password reset request was recently made for this account! Please check {user.email} for a reset email!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create a token that is only valid for 24 hours
            validity_period = settings.PASSWORD_RESET_TOKEN_VALIDITY_PERIOD
            token = create_password_reset_token(user, validity_period_in_hours=validity_period)
            message = construct_password_reset_mail(
                user=user, 
                password_reset_url=settings.PASSWORD_RESET_URL, 
                token=token,
                token_name=token_name,
                token_validity_period=validity_period
            )
            user.send_mail("Password Reset Request", message, html=True)
        except Exception as exc:
            log_exception(exc)
            if token:
                # Delete the created token if an error occurs
                delete_password_reset_token(token)
            return response.Response(
                data={
                    "status": "error",
                    "message": "An error occurred while processing your request. Please try again."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return response.Response(
            data={
                "status": "success",
                "message": f"Request processed successfully. An email has been sent to {user.email}."
            },
            status=status.HTTP_200_OK
        )



class CheckPasswordResetTokenValidity(views.APIView):
    """
    API View for checking if a user password reset token is still valid
    """
    http_method_names = ["post"]
    serializer_class = PasswordResetTokenSerializer
    permission_classes = (HasAPIKeyOrIsAuthenticated,)

    def post(self, request, *args, **kwargs) -> response.Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get("token")
        is_valid = check_password_reset_token_validity(token)

        if is_valid is False:
            # If the token is already invalid, delete it.
            delete_password_reset_token(token)
        return response.Response(
            data={
                "status": "success",
                "message": "Valid token" if is_valid else "Invalid token",
                "data": {
                    "valid": is_valid
                }
            },
            status=status.HTTP_200_OK
        )



class PasswordResetAPIView(views.APIView):
    """API view for resetting user account password"""
    http_method_names = ["post"]
    serializer_class = PasswordResetSerializer
    permission_classes = (HasAPIKeyOrIsAuthenticated,)

    def post(self, request, *args, **kwargs) -> response.Response:
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data.copy()
        new_password = data.pop("new_password")
        # The last item in the dictionary is the token
        token = list(data.values())[-1]
        token_is_valid = check_password_reset_token_validity(token)
        reset_successful = False
        
        if token_is_valid is False:
            # Delete the token so the user can request a password rest again
            delete_password_reset_token(token)
            return response.Response(
                data={
                    "status": "error",
                    "message": "The password reset token is invalid or has expired! Please request a password reset again."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reset_successful = reset_password_for_token(token, new_password)
        except Exception as exc:
            log_exception(exc)
            return response.Response(
                data={
                    "status": "error",
                    "message": "An error occurred while attempting password reset!"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        if not reset_successful:
            return response.Response(
                data={
                    "status": "error",
                    "message": "Password reset was unsuccessful! Please try again."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Log the user out of all devices after a successful password reset
        user = get_token_owner(token)
        if user:
            universal_logout(user)
        return response.Response(
            data={
                "status": "success",
                "message": "Password reset was successful!"
            },
            status=status.HTTP_200_OK
        )



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

        

class EMARecordListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating EMA records"""
    model = EMARecord
    serializer_class = EMARecordSerializer
    queryset = ema_record_qs
    permission_classes = (HasAPIKeyOrIsAuthenticated,) 
    # Tentative, this allows anyone with an apikey but not authtoken to create ema records

    def get_queryset(self) -> models.QuerySet[EMARecord]:
        ema_qs = super().get_queryset()
        try:
            ema_qs_filterer = EMARecordQSFilterer(self.request.query_params)
            return ema_qs_filterer.apply_filters(ema_qs)
        except Exception as exc:
            # Log the exception and return the unfiltered queryset
            log_exception(exc)
        return ema_qs
    

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
check_reset_token_validity_api_view = csrf_exempt(CheckPasswordResetTokenValidity.as_view())
password_reset_api_view = csrf_exempt(PasswordResetAPIView.as_view())

# Model API Views
currency_list_create_api_view = csrf_exempt(CurrencyListCreateAPIView.as_view())
currency_destroy_api_view = csrf_exempt(CurrencyDestroyAPIView.as_view())
ema_record_list_create_api_view = csrf_exempt(EMARecordListCreateAPIView.as_view())
