from typing import Any

from helpers.managers import SearchableModelManager, SearchableQuerySet


class CurrencyQuerySet(SearchableQuerySet):
    """Custom queryset for the `Currency` model."""

    def search(self, query: str | Any, fields: list[str] | str = None):
        if not fields:
            fields = ["name", "symbol", "category", "subcategory"]
        return super().search(query, fields)



class CurrencyManager(SearchableModelManager.from_queryset(CurrencyQuerySet)):
    '''Custom manager for the `Currency` model.'''
    pass

