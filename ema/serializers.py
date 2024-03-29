from rest_framework import serializers, exceptions
from typing import Any, Dict

from .models import EMARecord
from currency.serializers import CurrencySerializer
from currency.models import Currency



class EMARecordSerializer(serializers.ModelSerializer):
    """Model serializer for EMA records"""
    currency = CurrencySerializer(read_only=True)
    currency_symbol = serializers.CharField(write_only=True)

    class Meta:
        model = EMARecord
        fields = [
            "id",
            "timeframe",
            "currency",
            "currency_symbol",
            "close",
            "ema20",
            "ema50",
            "ema100",
            "ema200",
            "trend",
            "monhigh",
            "monlow",
            "monmid",
            "twenty_greater_than_fifty",
            "fifty_greater_than_hundred",
            "hundred_greater_than_twohundred",
            "close_greater_than_hundred",
            "timestamp",
            "updated_at",
        ]
        read_only_fields = ["timestamp", "updated_at"]
        extra_kwargs = {
            "trend": {"required": True},
            "timestamp": {"format": "%H:%M:%S %d-%m-%Y %z"},
            "updated_at": {"format": "%H:%M:%S %d-%m-%Y %z"},
        }

    def create(self, validated_data: Dict) -> Any:
        currency_symbol: str = validated_data.pop("currency_symbol", None)
        if not currency_symbol:
            raise exceptions.ValidationError({"currency_symbol": ["This field is required."]})
        
        try:
            currency = Currency.objects.get(symbol__iexact=currency_symbol)
        except Currency.DoesNotExist:
            raise exceptions.ValidationError({
                "currency_symbol": [f"Currency symbol provided, '{currency_symbol}', is not recognized."]
            })
        else:
            validated_data["currency"] = currency
        return super().create(validated_data)
