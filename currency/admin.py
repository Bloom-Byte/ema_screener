from django.contrib import admin

from .models import Currency, CurrencyCategory, CurrencySubcategory


admin.site.register(Currency)
admin.site.register(CurrencyCategory)
admin.site.register(CurrencySubcategory)
