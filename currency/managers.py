from typing import Any

from helpers.managers import SearchableModelManager, SearchableQuerySet


class CurrencyQuerySet(SearchableQuerySet):
    """Custom queryset for the `Currency` model."""

    def search(self, query: str | Any, fields: list[str] | str = None):
        """
        Search the queryset for the given query.

        :param query: The query to search for.
        :param fields: The fields to search in. If not provided, the default fields are used.
        The default fields are: ["symbol", "category", "subcategory"]
        """
        if not fields:
            fields = ["symbol", "category", "subcategory"]
        return super().search(query, fields)



class CurrencyManager(SearchableModelManager.from_queryset(CurrencyQuerySet)):
    '''Custom manager for the `Currency` model.'''
    pass

