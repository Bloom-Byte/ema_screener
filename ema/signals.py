from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete

from .models import EMARecord
from .serializers import EMARecordSerializer
from .utils import get_dict_diff, notify_group_of_ema_record_update_via_websocket



@receiver(pre_save, sender=EMARecord)
def send_updates_via_websocket(sender: type[EMARecord], instance: EMARecord, **kwargs) -> None:
    """
    Updates the frontend via websocket on changes to EMA records

    - A "create" code is sent when a new record is created alongside the new record data.

    - An "update" code is sent when an existing record is updated alongside the changes made to the record.
    """
    try:
        try:
            previous_record = EMARecord.objects.get(pk=instance.pk)
        except EMARecord.DoesNotExist:
            # It is a new record
            data = EMARecordSerializer(instance).data
            data = {
                "code": "create",
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
                "code": "update",
                "data": change_data
            }
            notify_group_of_ema_record_update_via_websocket("ema_record_updates", data)
    except Exception:
        # Ignore any errors that occur while sending the notification
        pass
    return



@receiver(post_delete, sender=EMARecord)
def send_deletes_via_websocket(sender: type[EMARecord], instance: EMARecord, **kwargs) -> None:
    """
    Notifies the frontend via websocket when an EMA record is deleted

    - A "delete" code is sent when a record is deleted alongside the id of the deleted record.
    """
    try:
        data = {
            "code": "delete",
            "data": {
                "id": str(instance.pk)
            }
        }
        notify_group_of_ema_record_update_via_websocket("ema_record_updates", data)
    except Exception:
        # Ignore any errors that occur while sending the notification
        pass
    return
