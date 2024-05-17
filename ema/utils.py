from typing import Dict
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



def get_dict_diff(dict1: Dict, dict2: Dict) -> Dict:
    """
    Get the changes between two dictionaries

    The changes in the values of the dictionaries are returned as a new dictionary
    """
    diff_dict = {}
    for key, value in dict1.items():
        if isinstance(value, dict):
            diff = get_dict_diff(value, dict2.get(key, {}))
            if diff:
                diff_dict[key] = diff
            continue
        
        dict2_value = dict2.get(key)
        if value == dict2_value:
            continue
        diff_dict[key] = dict2_value
    return diff_dict


WATCH_VALUES_INTERNAL_TO_EXTERNAL_NAME_MAPPING = {
    "twenty_greater_than_fifty": "20>50",
    "fifty_greater_than_hundred": "50>100",
    "hundred_greater_than_twohundred": "100>200",
    "close_greater_than_hundred": "close>100",
}

WATCH_VALUES_EXTERNAL_TO_INTERNAL_NAME_MAPPING = {
    "20>50": "twenty_greater_than_fifty",
    "50>100": "fifty_greater_than_hundred",
    "100>200": "hundred_greater_than_twohundred",
    "close>100": "close_greater_than_hundred",
}


def convert_watch_values_external_names_to_internal_names(data: Dict) -> Dict:
    """Converts external watchlist names to internal watchlist names"""
    new_data = {}
    for key, value in data.items():
        if key in WATCH_VALUES_EXTERNAL_TO_INTERNAL_NAME_MAPPING:
            internal_name = WATCH_VALUES_EXTERNAL_TO_INTERNAL_NAME_MAPPING[key]
            new_data[internal_name] = value
            continue
        new_data[key] = value   
    return new_data


def convert_watch_values_internal_names_to_external_names(data: Dict) -> Dict:
    """Converts internal watchlist names to external watchlist names"""
    new_data = {}
    for key, value in data.items():
        if key in WATCH_VALUES_INTERNAL_TO_EXTERNAL_NAME_MAPPING:
            external_name = WATCH_VALUES_INTERNAL_TO_EXTERNAL_NAME_MAPPING[key]
            new_data[external_name] = value
            continue
        new_data[key] = value
    return new_data


def notify_group_of_ema_record_update_via_websocket(group_name: str, data: Dict) -> None:
    """
    Notify the clients in the channel group of the EMA record update via websocket

    :param group_name: The name of the channel group to send the message to
    :param data: The data to send to the client
    """
    channel_layer = get_channel_layer("default")
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send.ema_record_update',
            'data': data
        }
    )
