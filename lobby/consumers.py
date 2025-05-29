import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .redis_client import client, list_lobbies


class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.userId = self.scope.get("user_id")
        await self.channel_layer.group_add("lobbies", self.channel_name)
        await self.accept()
        # отправляем начальные данные
        await self.send(json.dumps({"type": "init", "lobbies": list_lobbies()}))

        # подписываемся на Pub/Sub
        self.pubsub = client.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe("lobbies:updates")
        self.listen_task = asyncio.create_task(self.listen_pubsub())

    async def disconnect(self, close_code):
        if hasattr(self, "listen_task"):
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
                        print("update")
                        await self.send(
                            json.dumps({"type": "lobby_update", "data": data})
                        )

                    elif action == "start":
                        session_id = data.get("session_id")
                        players = data.get("players", [])

                        if self.userId and str(self.userId) in players:
                            await self.send(
                                json.dumps(
                                    {"type": "lobby_start", "session_id": session_id}
                                )
                            )
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass

    async def receive(self, text_data):
        pass
