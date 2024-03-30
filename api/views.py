from rest_framework import generics, response

from ema.models import EMARecord
from ema.serializers import EMARecordSerializer
from .utils import EMARecordFilterer

ema_record_qs = EMARecord.objects.select_related("currency").all()



class EMARecordListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating EMA records"""
    model = EMARecord
    serializer_class = EMARecordSerializer
    queryset = ema_record_qs

    def get_queryset(self):
        filterer = EMARecordFilterer(self.request.query_params)
        return filterer.apply_filters(super().get_queryset())
    

    def get(self, request, *args, **kwargs) -> response.Response:
        """
        Retrieve a list of EMA records

        Tne following query parameters are supported:
        - timeframe: Duration of the timeframe
        - currency: Symbol or name of the currency
        - ema20: EMA20 value
        - ema50: EMA50 value
        - ema100: EMA100 value
        - ema200: EMA200 value
        - trend: Trend direction (1 for upwards, -1 for downwards, 0 for sideways)

        """
        return super().get(request, *args, **kwargs)



ema_record_list_create_api_view = EMARecordListCreateAPIView.as_view()

