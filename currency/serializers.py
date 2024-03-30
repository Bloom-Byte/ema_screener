from rest_framework import serializers

from .models import Currency



class CurrencySerializer(serializers.ModelSerializer):
    """Model serializer for currencies"""
    category = serializers.CharField(source="category.name")
    subcategory = serializers.CharField(source="subcategory.name")

    class Meta:
        model = Currency
        fields = [
            "name",
            "symbol",
            "current_price",
            "category",
            "subcategory",
        ]


