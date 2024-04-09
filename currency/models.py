import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CurrencyManager


class Categories(models.TextChoices):
    """Choices for currency categories"""
    A = "A", _("A")
    B = "B", _("B")
    C = "C", _("C")
    D = "D", _("D")
    E = "E", _("E")


class Currency(models.Model):
    """Model for storing currencies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    symbol = models.CharField(max_length=10, unique=True)
    category = models.CharField(max_length=10, choices=Categories.choices)
    subcategory = models.CharField(max_length=100)
    exchange = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CurrencyManager()

    class Meta:
        ordering = ["symbol", '-added_at']
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self) -> str:
        return f"{self.symbol} ({self.exchange})"
    
