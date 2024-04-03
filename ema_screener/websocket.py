from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.conf import settings

from ema import routing as ema_routing
from .websocket_auth import APIKeyAuthMiddlewareStack


websocket_application = ProtocolTypeRouter({
    # websocket router for `ema` app
    "websocket": URLRouter(ema_routing.websocket_urlpatterns),
})


if settings.DEBUG is False:
    # In production, ensure that all connections to the websocket application are made with an API-KEY
    websocket_application = APIKeyAuthMiddlewareStack(websocket_application)
else:
    websocket_application = AuthMiddlewareStack(websocket_application)
