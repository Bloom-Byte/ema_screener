from django.conf import settings
from rest_framework import response, status, views
from typing import Dict
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt


from tokens.views import AuthTokenAuthenticationAPIView
from users.serializers import (
    PasswordResetRequestSerializer, PasswordResetSerializer, PasswordResetTokenSerializer
)
from users.password_reset import (
    check_if_password_reset_token_exists, check_password_reset_token_validity,
    create_password_reset_token, construct_password_reset_mail, 
    delete_password_reset_token, reset_password_for_token, get_token_owner
)
from api.authentication import universal_logout
from api.permission_mixins import AuthenticationRequired
from helpers.logging import log_exception



UserModel = get_user_model()


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
    


class UserLogoutAPIView(AuthenticationRequired, views.APIView):
    """
    API view for logging out a user. 

    This should be used when a user wants to logout of all devices.
    """
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs) -> response.Response:
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
                "message": f"{request.user} was logged out successfully!"
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



# User Authentication API Views
user_authentication_api_view = csrf_exempt(UserAuthenticationAPIView.as_view())
user_logout_api_view = csrf_exempt(UserLogoutAPIView.as_view())
password_reset_request_api_view = csrf_exempt(PasswordResetRequestAPIView.as_view())
check_reset_token_validity_api_view = csrf_exempt(CheckPasswordResetTokenValidity.as_view())
password_reset_api_view = csrf_exempt(PasswordResetAPIView.as_view())
