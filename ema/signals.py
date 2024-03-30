from django.dispatch import receiver
from django.db.models.signals import pre_save

from .models import EMARecord
from .serializers import EMARecordSerializer
from .utils import get_dict_diff



@receiver(pre_save, sender=EMARecord)
def send_updates_via_websocket(sender: type[EMARecord], instance: EMARecord, **kwargs) -> None:
    """
    Updates the frontend via websocket on changes to EMA records
    """
    try:
        previous_record = EMARecord.objects.get(pk=instance.pk)
    except EMARecord.DoesNotExist:
        # It is a new record
        data = EMARecordSerializer(instance).data
        # send data to frontend via websocket
        return
    
    previous_record_dict = EMARecordSerializer(previous_record).data
    record_dict = EMARecordSerializer(instance).data
    diff = get_dict_diff(previous_record_dict, record_dict)
    print(diff)
    # send diff to frontend via websocket
    return




    
