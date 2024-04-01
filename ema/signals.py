from django.dispatch import receiver
from django.db.models.signals import pre_save

from .models import EMARecord
from .serializers import EMARecordSerializer
from .utils import get_dict_diff, notify_group_of_ema_record_update_via_websocket



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
        data = {
            "message": "New EMA record added",
            "data": data
        }
        notify_group_of_ema_record_update_via_websocket("ema_record_updates", data)
        return
    
    previous_record_dict = EMARecordSerializer(previous_record).data
    record_dict = EMARecordSerializer(instance).data
    # Get the changes made to the record
    change_data = get_dict_diff(previous_record_dict, record_dict)
    if change_data:
        # Add the id of the record to the change_data
        change_data["id"] = str(instance.pk)
        data = {
            "message": "EMA record updated",
            "data": change_data
        }
        notify_group_of_ema_record_update_via_websocket("ema_record_updates", change_data)
    return




    
