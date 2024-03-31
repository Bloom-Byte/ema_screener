from django.db.models.manager import BaseManager
from rest_framework import generics, response, status
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse

from ema.models import EMARecord
from ema.serializers import EMARecordSerializer
from .filters import EMARecordFilterer

ema_record_qs = EMARecord.objects.select_related("currency").all()


@csrf_exempt
def health_check_api_view(request, *args, **kwargs) -> JsonResponse:
    """Simple view to test if the API server is up and running."""
    return JsonResponse(
        data={
            "message": "Server is !down."
        },
        status=status.HTTP_200_OK
    )



class EMARecordListCreateAPIView(generics.ListCreateAPIView):
    """API view for listing and creating EMA records"""
    model = EMARecord
    serializer_class = EMARecordSerializer
    queryset = ema_record_qs

    def get_queryset(self) -> BaseManager[EMARecord]:
        filterer = EMARecordFilterer(self.request.query_params)
        qs = super().get_queryset()
        return filterer.apply_filters(qs)
    

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
        - watch: EMA watchlist type. Can be either be type "A", "B", or "C"
        """
        return super().get(request, *args, **kwargs)



ema_record_list_create_api_view = EMARecordListCreateAPIView.as_view()

