from rest_framework import generics, exceptions

from ema.models import EMARecord
from ema.serializers import EMARecordSerializer
from .utils import EMARecordFilterer

ema_record_qs = EMARecord.objects.select_related("currency").all()



class EMARecordListCreateAPIView(generics.ListCreateAPIView):
    model = EMARecord
    serializer_class = EMARecordSerializer
    queryset = ema_record_qs

    def get_queryset(self):
        try:
            filterer = EMARecordFilterer(self.request.query_params)
        except Exception as exc:
            raise exceptions.ValidationError({"error": str(exc)})
        
        return filterer.apply_filters(super().get_queryset())



ema_record_list_create_api_view = EMARecordListCreateAPIView.as_view()

