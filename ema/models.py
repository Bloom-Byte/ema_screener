from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _


class TrendChoices(models.TextChoices):
    """Choices for trend direction"""
    UPWARDS = "1", _("Upwards")
    DOWNWORDS = "-1", _("Downwards")
    SIDEWAYS = "0", _("Sideways")



class EMARecord(models.Model):
    """Model for storing EMA records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timeframe = models.DurationField()
    currency = models.ForeignKey("currency.Currency", on_delete=models.CASCADE, related_name="ema_records")
    close = models.FloatField()
    ema20 = models.FloatField(null=True, blank=True)
    ema50 = models.FloatField(null=True, blank=True)
    ema100 = models.FloatField(null=True, blank=True)
    ema200 = models.FloatField(null=True, blank=True)
    trend = models.CharField(choices=TrendChoices.choices)
    monhigh = models.FloatField()
    monlow = models.FloatField()
    monmid = models.FloatField()
    twenty_greater_than_fifty = models.BooleanField()
    fifty_greater_than_hundred = models.BooleanField()
    hundred_greater_than_twohundred = models.BooleanField()
    close_greater_than_hundred = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = _("EMA Record")
        verbose_name_plural = _("EMA Records")


    def __str__(self) -> str:
        return f"{self.currency.symbol} at {self.timestamp.strftime('%H:%M:%S %d-%m-%Y (%Z)')}"
