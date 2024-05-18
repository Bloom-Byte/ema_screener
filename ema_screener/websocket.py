from channels.routing import ProtocolTypeRouter, URLRouter

from ema import routing as ema_routing
from .websocket_auth import APIKeyAuthMiddlewareStack


websocket_application = ProtocolTypeRouter({
    # websocket router for `ema` app
    "websocket": URLRouter(ema_routing.websocket_urlpatterns),
})


# websocket_application = APIKeyAuthMiddlewareStack(websocket_application)

