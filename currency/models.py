import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CurrencyManager


class Currency(models.Model):
    """Model for storing currencies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=10, unique=True)
    current_price = models.FloatField()
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    exchange = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CurrencyManager()

    class Meta:
        ordering = ["name", "symbol", '-added_at']
        unique_together = ["name", "symbol"]
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self) -> str:
        return f"{self.name} ({self.symbol}) - {self.exchange}"
    
