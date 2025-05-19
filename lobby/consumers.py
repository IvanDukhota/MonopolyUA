import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .redis_client import client, list_lobbies


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        await self.channel_layer.group_add("lobbies", self.channel_name)
        await self.accept()
        await self.send(json.dumps({"type": "init", "lobbies": list_lobbies()}))

        self.pubsub = client.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe("lobbies:updates")
        self.listen_task = asyncio.create_task(self.listen_pubsub())

    async def disconnect(self, close_code):
        self.listen_task.cancel()
        self.pubsub.unsubscribe("lobbies:updates")
        await self.channel_layer.group_discard("lobbies", self.channel_name)

    async def listen_pubsub(self):
        try:
            while True:
                message = self.pubsub.get_message()
                if message:
                    data = json.loads(message["data"])
                    action = data.get("action")

                    if action in ("create", "update", "kick", "remove"):
                        await self.send(
                            json.dumps({"type": "lobby_update", "data": data})
                        )
               
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass

    async def receive(self, text_data):
        pass
