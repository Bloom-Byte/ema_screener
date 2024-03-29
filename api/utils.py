from typing import Any, Dict, Mapping, TypeVar

from django.db import models


R = TypeVar("R", bound=models.Model)

class EMARecordFilterer:
    """Filters EMARecord queryset based on URL query parameters"""

    def __init__(self, querydict: Mapping[str, Any]) -> None:
        """
        Create a new instance of EMARecordFilterer

        :param querydict: QueryDict containing filters(query params) to be applied
        """
        self.filters = self.clean_querydict(querydict)

    @staticmethod
    def clean_querydict(querydict: Mapping[str, Any]) -> Dict[str, Any]:
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
                filter = getattr(EMARecordFilterer, f"clean_{key}")(value)
            except AttributeError:
                continue
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
    

