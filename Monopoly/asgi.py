"""
ASGI config for Monopoly project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Monopoly.settings")
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import lobby.routing, game.routing
from core.jwt_middleware import JwtAuthMiddleware
import asyncio
import threading

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JwtAuthMiddleware(
            URLRouter(
                lobby.routing.websocket_urlpatterns + 
                game.routing.websocket_urlpatterns
            )
        ),
    }
)

def _start_turn_manager_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    from game.turn_manager import monitor_all_games

    loop.create_task(monitor_all_games())
    loop.run_forever()

threading.Thread(target=_start_turn_manager_loop, daemon=True).start()