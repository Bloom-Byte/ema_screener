import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError as DjangoValidationError



class CurrencyCategory(models.Model):
    """Model for storing currency categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Currency Category")
        verbose_name_plural = _("Currency Categories")

    def __str__(self) -> str:
        return self.name



class CurrencySubcategory(models.Model):
    """Model for storing currency subcategories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(CurrencyCategory, on_delete=models.PROTECT, related_name="subcategories")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = _("Currency Subcategory")
        verbose_name_plural = _("Currency Subcategories")

    def __str__(self) -> str:
        return f"{self.name} ({self.category.name})"



class Currency(models.Model):
    """Model for storing currencies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=10, unique=True)
    current_price = models.FloatField()
    category = models.ForeignKey(CurrencyCategory, on_delete=models.PROTECT, related_name="currencies")
    subcategory = models.ForeignKey(CurrencySubcategory, on_delete=models.PROTECT, related_name="currencies")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "symbol"]
        unique_together = ["name", "symbol"]
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")

    def __str__(self) -> str:
        return f"{self.name} ({self.symbol})"
    

    def save(self, *args, **kwargs) -> None:
        self.symbol = self.symbol.upper()
        if not self.subcategory.category == self.category:
            raise DjangoValidationError({
                "subcategory": f"Subcategory '{self.subcategory.name}' does not belong to the category,'{self.category.name}'"
            })
        super().save(*args, **kwargs)
