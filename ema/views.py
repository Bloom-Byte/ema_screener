from django.db import models
from rest_framework import generics, response, status
from django.views.decorators.csrf import csrf_exempt


from .models import EMARecord
from .serializers import EMARecordSerializer
from .filters import EMARecordQSFilterer
from helpers.logging import log_exception


ema_record_qs = EMARecord.objects.select_related("currency").all()


class EMARecordListCreateAPIView(generics.ListCreateAPIView):
    """API view for retrieving, creating and updating EMA records"""
    model = EMARecord
    serializer_class = EMARecordSerializer
    queryset = ema_record_qs
    http_method_names = ["get", "post", "put"]

    def get_queryset(self) -> models.QuerySet[EMARecord]:
        ema_qs = super().get_queryset()
        try:
            ema_qs_filterer = EMARecordQSFilterer(self.request.query_params)
            return ema_qs_filterer.apply_filters(ema_qs)
        except Exception as exc:
            # Log the exception and return the unfiltered queryset
            log_exception(exc)
        return ema_qs
    

    def get(self, request, *args, **kwargs) -> response.Response:
        """
        Retrieve a list of EMA records

        Tne following query parameters are supported:
        - timeframe: Duration of the timeframe in the format "HH:MM:SS" e.g. "1:00:00" for 1 hour
        - currency: Symbol or name of the currency
        - ema20: EMA20 value
        - ema50: EMA50 value
        - ema100: EMA100 value
        - ema200: EMA200 value
        - trend: Trend direction (1 for upwards, -1 for downwards, 0 for sideways)
        - watch: EMA watchlist type. Can be either be type "A", "B", "C", "D", "E" or "F"
        """
        return super().get(request, *args, **kwargs)
    

    def put(self, request, *args, **kwargs) -> response.Response:
        """
        Update an EMA record
        """
        # User can update existing EMA records via a POST request already
        # Just add this so users can update records using a PUT request
        response = super().post(request, *args, **kwargs)
        # Change the status code to 200 if the record was updated successfully
        if response.status_code == status.HTTP_201_CREATED:
            response.status_code = status.HTTP_200_OK
        return response




ema_record_list_create_api_view = csrf_exempt(EMARecordListCreateAPIView.as_view())
