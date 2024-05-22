from typing import Dict, Union
from rest_framework_api_key.models import APIKey
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter



@database_sync_to_async
def api_key_is_valid(api_key: str) -> bool:
    """
    Check if an API key is valid.

    :param api_key: The API key to check
    :return: True if the API key exists, False otherwise
    """
    try:
        return APIKey.objects.is_valid(api_key)
    except APIKey.DoesNotExist:
        return False


def get_api_key_from_scope(scope: Dict) -> str | None:
    """
    Checks the websocket consumer scope headers and query-string for an API key.

    This function checks the headers for "X-API-KEY" key and the 
    query_string for the "api_key" key.

    :param scope: scope from websocket consumer
    :return: API key if found else, None.
    """
    query_string = scope["query_string"].decode("utf-8")
    if query_string:
        # Check query params for API key 
        query_params = parse_qs(query_string)
        api_key = query_params.get("api_key", None)
        if api_key:
            return api_key[0]
        
    else:
        # Check headers for API key
        headers = scope.get("headers", [])
        for header in headers:
            key = header[0].decode("utf-8")
            value = header[1].decode("utf-8")
            if key == "x-api-key":
                return value
    return None


UNAUTHORIZED_MSG = "Unauthorized! Ensure a valid API key is included in your connection request's header or url query params."

async def reject_unauthorized(send, message: str = UNAUTHORIZED_MSG) -> None:
    await send({
        "type": "websocket.close",
        "code": 403,
        "reason": message
    })
    return None



class APIKeyAuthMiddleware(BaseMiddleware):
    """
    Ensures that a valid API key is provided before accepting a connection

    The API key can be provided as:
    - A query parameter, `api_key`, or
    - A header, `X-API-KEY`
    """
    async def __call__(self, scope, receive, send):
        api_key = get_api_key_from_scope(scope)
        if not api_key:
            return await reject_unauthorized(send)

        authorized = await api_key_is_valid(api_key)
        if not authorized:
            return await reject_unauthorized(send)
        return await super().__call__(scope, receive, send)



def APIKeyAuthMiddlewareStack(inner: Union[URLRouter, ProtocolTypeRouter, BaseMiddleware]):
    """
    Applies both `channels.auth.AuthMiddlewareStack` and `APIKeyAuthMiddleware`
    """
    return APIKeyAuthMiddleware(AuthMiddlewareStack(inner))
