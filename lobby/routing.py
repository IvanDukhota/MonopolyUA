from django.urls import re_path
from .consumers import LobbyConsumer

websocket_urlpatterns = [
    re_path(r'ws/lobbies/$', LobbyConsumer.as_asgi()),
]