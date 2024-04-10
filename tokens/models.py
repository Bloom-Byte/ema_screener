from rest_framework_api_key.models import AbstractAPIKey
from rest_framework.authtoken.models import Token as BaseToken
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings



# Ensure "rest_framework.authtoken" is not included in settings.INSTALLED_APPS
class AuthToken(BaseToken):
    """Custom authentication token model"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="auth_token")

    class Meta(BaseToken.Meta):
        verbose_name = _("Auth Token")
        verbose_name_plural = _("Auth Tokens")



class PasswordResetToken(AbstractAPIKey):
    """Make shift password reset token model"""
    name = models.CharField(
        max_length=200,
        blank=False,
        default=None,
        help_text=(
            "A free-form name for the password reset token. "
            "Need not be unique. "
            "200 characters max."
        ),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_tokens")

    class Meta(AbstractAPIKey.Meta):
        verbose_name = _("Password Reset Token")
        verbose_name_plural = _("Password Reset Tokens")
        # Use a unique constraint to ensure that only one token per user is valid at a time
        unique_together = ["user", "hashed_key"]

