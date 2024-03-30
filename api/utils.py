from typing import Any, Dict, Mapping, TypeVar, Union
from rest_framework import request, exceptions

from django.db import models


R = TypeVar("R", bound=models.Model)

class EMARecordFilterer:
    """
    Filters EMARecord queryset based on URL query parameters


    Add a new method clean_<key> for each query parameter that needs to be cleaned and applied as a filter.
    Each clean_<key> method should accept a single argument and return a dictionary containing the filter

    Example:
    ```python
    class EMARecordFilterer:
        ...
        @staticmethod
        def clean_new_param(value: str) -> Dict[str, Any]:
            # Convert value to appropriate type and 
            # return a dictionary containing the filter
            return {"new_param": value}
    """
    def __init__(self, querydict: Union[request.QueryDict, Mapping[str, Any]]) -> None:
        """
        Create a new instance of EMARecordFilterer

        :param querydict: QueryDict containing filters(query params) to be applied
        """
        self.filters = self.clean_querydict(querydict)
    
    
    def clean_querydict(self, querydict: Union[request.QueryDict, Mapping[str, Any]]) -> Dict[str, Any]:
        """
        Clean querydict by removing unwanted keys and converting values to appropriate key-value pairs
        that can be used to filter queryset.

        The querydict is cleaned by calling appropriate clean_<key> method for each key in the querydict.

        :param querydict: QueryDict containing filters(query params) to be applied
        :return: Cleaned querydict
        """
        cleaned = {}
        for key, value in querydict.items():
            try:
                filter = getattr(self, f"clean_{key}")(value)
            except AttributeError:
                continue
            except Exception as exc:
                exceptions.ValidationError({
                    "error": f"Error while cleaning '{key}' query parameter: {str(exc)}"
                })
            else:
                if not isinstance(filter, dict):
                    raise TypeError(f"clean_{key} method must return a dictionary")
                cleaned.update(filter)
        return cleaned
            

    def apply_filters(self, qs: models.QuerySet[R]) -> models.QuerySet[R]:
        """
        Apply filters to queryset

        :param qs: EMARecord queryset
        :return: Filtered EMARecord queryset
        """
        return qs.filter(**self.filters)
    
    @staticmethod
    def clean_ema20(value: str) -> Dict[str, float]:
        return {"ema20": float(value)}
    
    @staticmethod
    def clean_ema50(value: str) -> Dict[str, float]:
        return {"ema50": float(value)}
    
    @staticmethod
    def clean_ema100(value: str) -> Dict[str, float]:
        return {"ema100": float(value)}
    
    @staticmethod
    def clean_ema200(value: str) -> Dict[str, float]:
        return {"ema200": float(value)}
    
    @staticmethod
    def clean_currency(value: str) -> Dict[str, str]:
        return {
            "currency__symbol__iexact": value,
            "currency__name__iexact": value,
        }
    
    @staticmethod
    def clean_timeframe(value: str) -> Dict[str, str]:
        return {"timeframe": value}
    
    @staticmethod
    def clean_trend(value: str) -> Dict[str, int]:
        return {"trend": int(value)}
    
    @staticmethod
    def clean_tgf_and_fgh(value: str) -> Dict[str, bool]:
        return {
            "twenty_greater_than_fifty": value.lower() == "true",
            "fifty_greater_than_hundred": value.lower() == "true",
            "hundred_greater_than_twohundred": False,
            "close_greater_than_hundred": False,
        }
    
    @staticmethod
    def clean_fgh_and_hgt(value: str) -> Dict[str, bool]:
        return {
            "fifty_greater_than_hundred": value.lower() == "true",
            "hundred_greater_than_twohundred": value.lower() == "true",
            "close_greater_than_hundred": False,
            "twenty_greater_than_fifty": False,
        }

