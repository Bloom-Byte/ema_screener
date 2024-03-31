from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from ema import routing as ema_routing


application = ProtocolTypeRouter({
    "websocket": URLRouter(ema_routing.websocket_urlpatterns),
})
