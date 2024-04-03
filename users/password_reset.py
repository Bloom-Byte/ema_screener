from django.urls import reverse
from django.template.loader import render_to_string
from django.conf import settings
from django.http.request import HttpRequest
import datetime
from django.utils import timezone

from .models import UserAccount, PasswordResetToken


def check_if_password_reset_token_exists(user: UserAccount) -> bool:
    """Check if a password reset token already exists for the given user."""
    return PasswordResetToken.objects.filter(user=user).exists()


def create_password_reset_token(user: UserAccount, validity_period_in_hours: int = None) -> str:
    """Create a password reset token for the given user."""
    if validity_period_in_hours is not None:
        validity_period = datetime.timedelta(hours=validity_period_in_hours)
        expiry_date = timezone.now() + validity_period
    else:
        expiry_date = None

    _, token = PasswordResetToken.objects.create_key(
        user=user, 
        name=f"Password reset token for {user.email}",
        expiry_date=expiry_date
    )
    return token


def check_password_reset_token_validity(token: str) -> bool:
    """Check if the password reset token is valid."""
    reset_token = PasswordResetToken.objects.get_from_key(token)
    if reset_token and reset_token.has_expired is False:
        return True
    return False


def construct_password_reset_mail(user: UserAccount, request: HttpRequest, token: str) -> str:
    """Construct the password reset mail body for the given user."""
    reset_link = request.build_absolute_uri(reverse('api-v1:account__password-reset', kwargs={'token': token}))
    context = {
        "webapp_name": settings.SITE_NAME,
        "email": user.email,
        "reset_link": reset_link,
    }
    return render_to_string("emails/password_reset_mail.html", context)


def send_password_reset_mail(user: UserAccount, request: HttpRequest, token: str) -> None:
    """Send password reset email to the user."""
    user.send_mail(
        subject="Password Reset Request",
        message=construct_password_reset_mail(user, request, token),
        html=True
    )
