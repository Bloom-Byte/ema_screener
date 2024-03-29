from rest_framework import serializers

from .models import Currency



class CurrencySerializer(serializers.ModelSerializer):
    """Model serializer for currencies"""
    category = serializers.StringRelatedField()
    subcategory = serializers.StringRelatedField()

    class Meta:
        model = Currency
        fields = [
            "name",
            "symbol",
            "current_price",
            "category",
            "subcategory",
        ]


