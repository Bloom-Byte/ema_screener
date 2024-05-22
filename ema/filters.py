import functools
from typing import Any, List, Mapping, Generator
import itertools
from django.db import models
from django.utils.dateparse import parse_duration

from helpers.queryset_filterers import QueryDictQuerySetFilterer


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
@functools.cache
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




class EMARecordQSFilterer(QueryDictQuerySetFilterer):
    """Filters EmaRecord queryset by request query dict"""
    def parse_ema20(self, value: str) -> models.Q:
        return models.Q(ema20=float(value))
    
    def parse_ema50(self, value: str) -> models.Q:
        return models.Q(ema50=float(value)) 
    
    def parse_ema100(self, value: str) -> models.Q:
        return models.Q(ema100=float(value))

    def parse_ema200(self, value: str) -> models.Q:
        return models.Q(ema200=float(value))
    
    def parse_currency(self, value: str) -> models.Q:
        return models.Q(currency__symbol__iexact=value) | models.Q(currency__exchange__iexact=value)
    
    def parse_timeframe(self, value: str) -> models.Q:
        return models.Q(timeframe=parse_duration(value))
    
    def parse_trend(self, value: str) -> models.Q:
        return models.Q(trend=int(value))
    
    def parse_watch(self, value: str) -> models.Q:
        q = models.Q()
        # If value is 'sideways', add all possible sideways watch filters
        if value.lower().strip() == "sideways":
            for filter in sideways_watch_filters():
                q.add(models.Q(**filter), models.Q.OR)
        else:
            filters = WATCH_VALUE_QUERY_FILTERS.get(value.upper().strip(), None)
            if filters is None:
                raise self.ParseError([f"Invalid value '{value}' for watch parameter"])
            q = models.Q(**filters)
        return q
    
    def parse_category(self, value: str) -> models.Q:
        return models.Q(currency__category__iexact=value)
    
    def parse_subcategory(self, value: str) -> models.Q:
        return models.Q(currency__subcategory__iexact=value)

