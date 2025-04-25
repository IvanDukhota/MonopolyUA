import json
from .models import GameSession, Player
from .redis import (
    save_player_state,
    get_player_state,
    append_chat_message,
    get_chat_messages,
    get_username_from_token
)
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from urllib.parse import parse_qs, unquote


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope["url_route"]["kwargs"]["session_id"]

        token = self.scope["query_string"].decode().split("token=")[-1]
        self.nickname = get_username_from_token(token) or "Unknown"

        self.room_group_name = f"game_{self.session_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        self.session = await self.get_or_create_session()
        self.player = await self.get_or_create_player()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_message",
                "message": f"приєднтися до гри.",
                "nickname": self.player.nickname,
                "timestamp": datetime.now().isoformat(),
            },
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data.get("type") == "move":
            steps = data.get("steps", 0)
            state = get_player_state(self.session_id, self.nickname)
            new_position = (state.get("position", 0) + steps) % 40
            state["position"] = new_position
            save_player_state(self.session_id, self.nickname, state)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "game_message",
                    "message": f"{self.nickname} кинув кубики і перемістився на {new_position} клітку.",
                },
            )
        elif data.get("type") == "chat":
            msg = {
                "nickname": self.nickname,
                "message": data.get("message"),
            }
            append_chat_message(self.session_id, msg)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": msg,
                },
            )

    async def game_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "nickname": event["nickname"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat",
                    "message": event["message"],
                }
            )
        )

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
        return Player.objects.create(
            session=session, nickname=self.nickname, order=order
        )

    @database_sync_to_async
    def move_player(self, steps):
        self.player.position += steps
        self.player.position %= 40
        self.player.save()
        return self.player.position
