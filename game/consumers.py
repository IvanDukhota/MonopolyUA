import json
from .models import GameSession, Player
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.nickname = self.scope["query_string"].decode().split("=")[-1] or "Unknown"

        self.room_group_name = f"game_{self.session_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        self.session = await self.get_or_create_session()
        self.player = await self.get_or_create_player()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_message",
                "message": f"{self.player.nickname} приєднтися до гри.",
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "move":
            steps = data.get("steps", 0)
            new_pos = await self.move_player(steps)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_message",
                    "message": f"{self.player.nickname} кинув кубики і перемістився на {new_pos} клітку.",
                }
            )

    async def game_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))

    @database_sync_to_async
    def get_or_create_session(self):
        return GameSession.objects.get_or_create(id=self.session_id)[0]

    @database_sync_to_async
    def get_or_create_player(self):
        session = GameSession.objects.get(id=self.session_id)
        existing = session.players.filter(nickname=self.nickname).first()
        if existing:
            return existing
        order = session.players.count()
        return Player.objects.create(session=session, nickname=self.nickname, order=order)

    @database_sync_to_async
    def move_player(self, steps):
        self.player.position += steps
        self.player.position %= 40
        self.player.save()
        return self.player.position
