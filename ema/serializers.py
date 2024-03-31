from rest_framework import serializers, exceptions
from typing import Any, Dict

from .models import EMARecord
from currency.serializers import CurrencySerializer
from currency.models import Currency
from .utils import (
    convert_watch_values_external_names_to_internal_names,
    convert_watch_values_internal_names_to_external_names
)



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

    def to_representation(self, instance) -> Dict:
        representation = super().to_representation(instance)
        # Convert internal watchlist names to external watchlist names
        # before returning the data
        return convert_watch_values_internal_names_to_external_names(representation)
    

    def run_validation(self, data=...):
        # Incase the watch values are provided in external names,
        # convert the external watch value names to internal watchlist names
        # before validating the data
        data = convert_watch_values_external_names_to_internal_names(data)
        return super().run_validation(data)


    def create(self, validated_data: Dict) -> Any:
        currency_symbol: str = validated_data.pop("currency_symbol", None)
        if not currency_symbol:
            raise exceptions.ValidationError({
                "currency_symbol": ["This field is required."]
            })
        
        try:
            currency = Currency.objects.get(symbol__iexact=currency_symbol)
        except Currency.DoesNotExist:
            raise exceptions.ValidationError({
                "currency_symbol": [f"Currency symbol provided, '{currency_symbol}', is not recognized."]
            })
        else:
            validated_data["currency"] = currency
        return super().create(validated_data)

