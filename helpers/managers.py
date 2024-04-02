from __future__ import annotations
from typing import Any, TypeVar, Union, List
from django.db import models


M = TypeVar("M", bound=models.Model)

class SearchableQuerySet[M](models.QuerySet):
    """A model queryset that supports search"""
    model: M
    
    def search(self, query: Union[str, Any], fields: Union[List[str], str]) -> SearchableQuerySet[M]:
        """
        Search the queryset for the given query in the given fields.

        :param query: The search query.
        :param fields: The fields to search in.
        :return: A queryset containing the search results.
        """
        if isinstance(fields, str):
            fields = [fields,]

        query = query.strip()
        if not query:
            return self.none()
        
        q = models.Q()
        for field in fields:
            q = q | models.Q(**{f"{field}__icontains": query})
        return self.filter(q).distinct()



class SearchableModelManager[M](models.Manager.from_queryset(SearchableQuerySet)):
    """A model manager that supports search"""
    model: M

    def get_queryset(self) -> SearchableQuerySet[M]:
        return super().get_queryset()
    
    
    def search(self, query: Union[str, Any], fields: Union[List[str], str]) -> SearchableQuerySet[M]:
        """
        Search the model for the given query in the given fields.

        :param query: The search query.
        :param fields: The fields to search in.
        :return: A queryset containing the search results.
        """
        return self.get_queryset().search(query=query, fields=fields)
