import functools
from typing import Any, List, Mapping, TypeVar, Union, Generator
from rest_framework import request, exceptions
import itertools

from django.db import models
from django.db.models.manager import BaseManager


WATCH_VALUE_QUERY_FILTERS = {
    # MUST WATCH
    "A": {
        "twenty_greater_than_fifty": True,
        "fifty_greater_than_hundred": True,
        "hundred_greater_than_twohundred": False,
        "close_greater_than_hundred": False,
    },
    # BUY
    "B": {
        "twenty_greater_than_fifty": True,
        "fifty_greater_than_hundred": True,
        "hundred_greater_than_twohundred": True,
        "close_greater_than_hundred": False,
    },
    # STRONG BUY
    "C": {
        "twenty_greater_than_fifty": True,
        "fifty_greater_than_hundred": True,
        "hundred_greater_than_twohundred": True,
        "close_greater_than_hundred": True,
    },
    # NEGATIVE WATCH
    "D": {
        "twenty_greater_than_fifty": False,
        "fifty_greater_than_hundred": False,
        "hundred_greater_than_twohundred": True,
        "close_greater_than_hundred": True,
    },
    # DOWN
    "E": {
        "twenty_greater_than_fifty": False,
        "fifty_greater_than_hundred": False,
        "hundred_greater_than_twohundred": False,
        "close_greater_than_hundred": True,
    },
    # STRONG DOWN
    "F": {
        "twenty_greater_than_fifty": False,
        "fifty_greater_than_hundred": False,
        "hundred_greater_than_twohundred": False,
        "close_greater_than_hundred": False,
    }
}



# cache the results of possible_selections so that 
# we don't have to repeat the same calculations
# which might be expensive
@functools.lru_cache(maxsize=10)
def possible_selections(*args, r) -> List[tuple]:
    """
    Utility function to get all possible selections of r items from the input list
    including duplicates.

    :param args: List of items to choose from
    :param r: Number of items to choose
    """
    return list(itertools.combinations_with_replacement(args, r))


def possible_watch_filters() -> Generator[Mapping[str, Any], None, None]:
    """Generate all possible watch filters"""
    # Assuming the combination set is (True, True, False, False) repeated twice
    combination_set = (True, True, False, False)*2
    # How many possible combinations of 4 can be made from the combination set
    # that is, how many ways can we choose 4 items from the combination set.
    # The result is 70, but remove duplicates
    eight_combinate_four_without_duplicates = set(possible_selections(*combination_set, r=4))
    for values in eight_combinate_four_without_duplicates:
        filters = {
            "twenty_greater_than_fifty": values[0],
            "fifty_greater_than_hundred": values[1],
            "hundred_greater_than_twohundred": values[2],
            "close_greater_than_hundred": values[3],
        }
        yield filters


def sideways_watch_filters():
    """Generate all possible sideways watch filters"""
    none_sideways_watch_filters = WATCH_VALUE_QUERY_FILTERS.values()
    for filter in possible_watch_filters():
        if filter not in none_sideways_watch_filters:
            yield filter



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
    ```

    If there is an error you should raise a `rest_framework.exceptions.ValidationError` with a dictionary containing the error message.

    For example:
    ```python
    raise exceptions.ValidationError({
        "new_param": ["Invalid value for new_param"]
    })
    ```
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
            if not value:
                # Skip empty values
                continue
            try:
                query_filter = getattr(self, f"parse_{key}")(value)
            except AttributeError:
                # Method for parsing the query parameter was not implemented
                continue
            except Exception as exc:
                exceptions.ValidationError({
                    "non_field_errors": [f"Error while parsing '{key}' query parameter: {str(exc)}"]
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
        return models.Q(currency__symbol__iexact=value) | models.Q(currency__exchange__iexact=value)
    
    @staticmethod
    def parse_timeframe(value: str) -> models.Q:
        return models.Q(timeframe=value)
    
    @staticmethod
    def parse_trend(value: str) -> models.Q:
        return models.Q(trend=int(value))
    
    @staticmethod
    def parse_watch(value: str) -> models.Q:
        q = models.Q()
        # If value is 'sideways', add all possible sideways watch filters
        if value.lower().strip() == "sideways":
            for filter in sideways_watch_filters():
                q.add(models.Q(**filter), models.Q.OR)
        else:
            filters = WATCH_VALUE_QUERY_FILTERS.get(value.upper().strip(), None)
            if filters is None:
                raise exceptions.ValidationError({
                    "watch": [f"Invalid value '{value}' for watch parameter"]
                })
            q = models.Q(**filters)
        return q

