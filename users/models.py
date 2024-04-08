from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
import uuid
from typing import Any
from django.utils.translation import gettext_lazy as _
from django.core.mail import EmailMessage, get_connection as get_smtp_connection

from .managers import UserAccountManager



class UserAccount(PermissionsMixin, AbstractBaseUser):
    """Custom user model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    is_active = models.BooleanField(_("active") ,default=True)
    is_admin = models.BooleanField(_("admin") ,default=False)
    is_staff = models.BooleanField(_("staff") ,default=False)
    is_superuser = models.BooleanField(_("superuser") ,default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    objects = UserAccountManager()

    class Meta:
        verbose_name = _("User account")
        verbose_name_plural = _("User accounts")
        ordering = ["-registered_at"]

    def __str__(self) -> str:
        return self.email
    
    
    def send_mail(
        self, 
        subject: str, 
        message: str, 
        from_email: str = settings.DEFAULT_FROM_EMAIL, 
        connection: Any | None = None,
        html: bool = False
    ) -> None:
        """
        Send email to user.
        
        :param subject: The subject of the email.
        :param message: The message to send.
        :param from_email: The email address to send from.
        :param connection: The email connection to use.
        :param html: Whether the message is an html message.
        """
        connection = connection or get_smtp_connection()
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=f"{settings.SITE_NAME} <{from_email}>",
            to=[self.email],
            connection=connection
        )
        if html:
            email.content_subtype = "html"
        email.send(fail_silently=False)
        return None

