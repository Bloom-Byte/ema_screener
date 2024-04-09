from rest_framework import serializers

from .models import Currency



class CurrencySerializer(serializers.ModelSerializer):
    """Model serializer for `Currency` model"""
    class Meta:
        model = Currency
        fields = [
            "id",
            "symbol",
            "category",
            "subcategory",
            "exchange",
            "added_at",
            "updated_at",
        ]
        read_only_fields = ["id", "added_at", "updated_at"]
        extra_kwargs = {
            "added_at": {"format": "%H:%M:%S %d-%m-%Y %z"},
            "updated_at": {"format": "%H:%M:%S %d-%m-%Y %z"},
        }



class StrippedCurrencySerializer(serializers.ModelSerializer):
    """Stripped down version of the `Currency` model serializer"""
    class Meta:
        model = Currency
        exclude = ["id", "added_at", "updated_at"]
        
