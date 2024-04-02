from typing import Any, Mapping, TypeVar, Union
from rest_framework import request, exceptions

from django.db import models
from django.db.models.manager import BaseManager


M = TypeVar("M", bound=models.Model)

class EMARecordQSFilterer:
    """
    Filters EMARecord queryset based on URL query parameters


    Add a new method `parse_<key>` for each query parameter that needs to be parsed and applied as a filter.
    Each `parse_<key>` method should accept a single argument and return a `django.db.models.Q` object representing
    the filter to be applied. The `parse_<key>` method should raise an `rest_framework.exceptions.ValidationError` if the value
    is invalid or cannot be parsed.

    Example:
    ```python
    class EMARecordFilterer:
        ...
        @staticmethod
        def parse_new_param(value: str) -> models.Q:
            # Convert value to appropriate type and 
            # return a dictionary containing the filter
            return models.Q(new_param=value)
    """
    def __init__(self, querydict: Union[request.QueryDict, Mapping[str, Any]]) -> None:
        """
        Create a new instance of EMARecordFilterer

        :param querydict: QueryDict containing filters(query params) to be applied
        """
        self.q = self.parse_querydict(querydict)
    
    
    def parse_querydict(self, querydict: Union[request.QueryDict, Mapping[str, Any]]) -> models.Q:
        """
        Clean and parse querydict containing filters

        This method iterates over each key-value pair in the querydict and calls the corresponding
        `parse_<key>` method to clean and parse the value. The cleaned query filters are then combined
        using the AND operator.

        :param querydict: QueryDict containing filters(query params) to be applied
        :return: Combined query filters
        """
        aggregate = models.Q()
        for key, value in querydict.items():
            try:
                query_filter = getattr(self, f"parse_{key}")(value)
            except AttributeError:
                # Method for parsing the query parameter was not implemented
                continue
            except Exception as exc:
                exceptions.ValidationError({
                    "error": f"Error while cleaning '{key}' query parameter: {str(exc)}"
                })
            else:
                if not isinstance(query_filter, models.Q):
                    raise TypeError(
                        f"parse_{key} method must return a `django.db.models.Q` object."
                    )
                aggregate.add(query_filter, models.Q.AND)
        return aggregate
            

    def apply_filters(self, qs: BaseManager[M]) -> BaseManager[M]:
        """
        Apply query filters to queryset

        :param qs: Unfiltered EMARecord queryset
        :return: Filtered EMARecord queryset
        """
        return qs.filter(self.q)
    
    @staticmethod
    def parse_ema20(value: str) -> models.Q:
        return models.Q(ema20=float(value))
    
    @staticmethod
    def parse_ema50(value: str) -> models.Q:
        return models.Q(ema50=float(value)) 
    
    @staticmethod
    def parse_ema100(value: str) -> models.Q:
        return models.Q(ema100=float(value))

    @staticmethod
    def parse_ema200(value: str) -> models.Q:
        return models.Q(ema200=float(value))
    
    @staticmethod
    def parse_currency(value: str) -> models.Q:
        return models.Q(currency__symbol__iexact=value) | models.Q(currency__name__iexact=value)
    
    @staticmethod
    def parse_timeframe(value: str) -> models.Q:
        return models.Q(timeframe=value)
    
    @staticmethod
    def parse_trend(value: str) -> models.Q:
        return models.Q(trend=int(value))
    
    @staticmethod
    def parse_watch(value: str) -> models.Q:
        filters = WATCH_VALUE_QUERY_FILTERS.get(value.upper(), None)
        if filters is None:
            raise exceptions.ValidationError({
                "watch": f"Invalid value '{value}' for watch parameter"
            })
        return models.Q(**filters)



WATCH_VALUE_QUERY_FILTERS = {
    "A": {
        "twenty_greater_than_fifty": True,
        "fifty_greater_than_hundred": True,
        "hundred_greater_than_twohundred": False,
        "close_greater_than_hundred": False,
    },
    "B": {
        "twenty_greater_than_fifty": True,
        "fifty_greater_than_hundred": True,
        "hundred_greater_than_twohundred": True,
        "close_greater_than_hundred": False,
    },
    "C": {
        "twenty_greater_than_fifty": True,
        "fifty_greater_than_hundred": True,
        "hundred_greater_than_twohundred": True,
        "close_greater_than_hundred": True,
    }
}
