import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .redis_client import (
    client,
    get_game_state,
    append_chat_message,
    process_player_move,
    create_game_log,
    buy_property,
    get_next_turn_and_log,
    pay_rent,
    process_utility_payment
)


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):

        self.user_id = self.scope.get("user_id")
        if not (self.user_id):
            await self.close(code=4001)
            return

        qs = self.scope.get("query_string", b"").decode()
        params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
        self.session_id = params.get("session")
        if not self.session_id:
            await self.close(code=4002)
            return

        state = await asyncio.get_event_loop().run_in_executor(
            None, lambda: get_game_state(self.session_id)
        )
        if str(self.user_id) not in state["players"]:
            await self.close(code=4003)
            return

        self.group_name = f"game_{self.session_id}"
        self.user_group = f"user_{self.user_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()

        await self.send(
            json.dumps({"type": "init", "state": state, "user_id": str(self.user_id)})
        )

        current = state["meta"].get("current_turn")
        if current and str(self.user_id) == current:
            await self.send(json.dumps({"type": "turn_start"}))

        self.pubsub = client.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(f"game:{self.session_id}:updates")
        self.listen_task = asyncio.create_task(self.listen_pubsub())

    async def disconnect(self, close_code):
        if hasattr(self, "listen_task"):
            self.listen_task.cancel()

        if hasattr(self, "pubsub"):
            self.pubsub.unsubscribe(f"game:{self.session_id}:updates")

        await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def listen_pubsub(self):
        try:
            while True:
                message = self.pubsub.get_message()
                if message and message.get("data"):
                    data = json.loads(message["data"])
                    action = data.get("action")

                    if action == "log":
                        await self.send(
                            text_data=json.dumps(
                                {
                                    "type": "log",
                                    "message": data["message"],
                                    "timestamp": data["timestamp"],
                                }
                            )
                        )

                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass


    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            msg = json.loads(text_data)

            if msg.get("type") == "make_move":
                die1, die2 = msg["move"]["dice"]
                try:
                    result = process_player_move(
                        self.session_id, self.user_id, die1, die2
                    )
                except ValueError:
                    return

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_move",
                        "data": {
                            "user_id": result["user_id"],
                            "from": result["from"],
                            "to": result["to"],
                            "color": result["color"],
                        },
                    },
                )

                log_entry = result["log"]
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message":   log_entry["message"],
                    },
                )
                

                prop_key = f"game:{self.session_id}:property:{result['to']}"
                player_key = f"game:{self.session_id}:player:"

                prop = client.hgetall(prop_key)
                ptype = prop.get("type")
                owner_id = prop.get("owner")

                if ptype in ("company", "automaker", "utility"):

                    if owner_id and owner_id != result["user_id"]:
                        amount = 0

                        if ptype == "company":
                            rents = json.loads(prop["rent"])
                            houses = int(prop.get("houses", 0))
                            amount = rents[houses]

                        elif ptype == "automaker":
                            automaker_keys = client.keys(
                                f"game:{self.session_id}:property:*"
                            )
                            count = 0
                            for key in automaker_keys:
                                p = client.hgetall(key)
                                if (
                                    p.get("type") == "automaker"
                                    and p.get("owner") == owner_id
                                ):
                                    count += 1
                            rents = json.loads(prop["rent"])
                            amount = (
                                rents[count - 1]
                                if 1 <= count <= len(rents)
                                else rents[-1]
                            )

                        elif ptype == "utility":

                            util_count = 0
                            for key in client.keys(
                                f"game:{self.session_id}:property:*"
                            ):
                                p = client.hgetall(key)
                                if (
                                    p.get("type") == "utility"
                                    and p.get("owner") == owner_id
                                ):
                                    util_count += 1

                            multiplier = 4 if util_count == 1 else 10

                            await self.send(
                                text_data=json.dumps(
                                    {
                                        "type": "property_action",
                                        "action": "roll_for_utility",
                                        "property_id": result["to"],
                                        "multiplier": multiplier,
                                        "owner": owner_id,
                                        "owner_name": client.hget(
                                            player_key + prop["owner"], "username"
                                        ),
                                    }
                                )
                            )
                            return

                        await self.channel_layer.group_send(
                            self.user_group,
                            {
                                "type": "property_action",
                                "action": "pay_rent",
                                "property_id": result["to"],
                                "property_name": prop["name"],
                                "amount": amount,
                                "owner": owner_id,
                                "owner_name": client.hget(
                                    player_key + prop["owner"], "username"
                                ),
                            },
                        ) 

                    elif not owner_id:
                        await self.channel_layer.group_send(
                            self.user_group,
                            {
                                "type": "property_action",
                                "action": "offer_buy",
                                "property_id": result["to"],
                                "property_name": prop["name"],
                                "price": prop["buy_price"],
                            },
                        )

                    elif owner_id and owner_id == result["user_id"]:
                        xxx

                elif ptype == "side":
                    print("side")

            elif msg.get("type") == "confirm_buy":
                property_id = msg.get("property_id")
                property_name = msg.get("property_name")
                try:
                    update = buy_property(self.session_id, self.user_id, property_id, property_name)
                except ValueError as e:
                    await self.send(
                        text_data=json.dumps({"type": "error", "message": str(e)})
                    )
                    return
            
                await self.channel_layer.group_send(
                    self.group_name, {"type": "game_property_update", "data": update}
                )
                
                log_entry = update["log"]
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": log_entry["message"]
                    },
                )

                info = get_next_turn_and_log(self.session_id)

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": info["log"]["message"],
                    }
                )

                await self.channel_layer.group_send(
                    f"user_{info['next_turn']}",
                    {"type": "your_turn"}
                )

            elif msg.get("type") == "decline_buy":
                property_id   = msg.get("property_id")
                property_name = msg.get("property_name")

                username = client.hget(f"game:{self.session_id}:player:{self.user_id}", "username") or str(self.user_id)
                decline_message = f"{username} відмовився купувати власність {property_id} «{property_name}»."
                decline_log = create_game_log(self.session_id, decline_message)

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": decline_log["message"]
                    }
                )

                info = get_next_turn_and_log(self.session_id)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": info["log"]["message"],
                    }
                )
                
                await self.channel_layer.group_send(
                    f"user_{info['next_turn']}",
                    {"type": "your_turn"}
                )

            elif msg.get("type") == "confirm_pay_rent":
                owner   = msg["owner"]
                amount  = int(msg["amount"])

                result = pay_rent(self.session_id, str(self.user_id), owner, amount)

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_balance_update",
                        "balances": {
                            result["payer_id"]: result["payer_balance"],
                            result["owner_id"]: result["owner_balance"],
                        },
                    }
                )

                log_entry = result["log"]
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": log_entry["message"]
                    }
                )

                info = get_next_turn_and_log(self.session_id)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": info["log"]["message"]
                    }
                )

                await self.channel_layer.group_send(
                    f"user_{info['next_turn']}",
                    {"type": "your_turn"}
                )

            if msg.get("type") == "confirm_pay_utility":
                payer = str(self.user_id)
                owner = msg["owner"]
                amount = int(msg["amount"])
                sum = int(msg["sum"])
                multiplier = int(msg["multiplier"])

                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: process_utility_payment(self.session_id, payer, owner, amount, sum, multiplier)
                    )
                except ValueError as e:
                    await self.send(text_data=json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
                    return

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_balance_update",
                        "balances": result["balances"],
                    }
                )

                log_entry = result["log"]
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": log_entry["message"],
                    }
                )

                info = get_next_turn_and_log(self.session_id)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": info["log"]["message"],
                        "timestamp": info["log"]["timestamp"],
                    }
                )
                await self.channel_layer.group_send(
                    f"user_{info['next_turn']}",
                    {"type": "your_turn"}
                )

            elif msg.get("type") == "chat":
                text = msg.get("text", "").strip()
                if not text:
                    return

                chat_obj = append_chat_message(self.session_id, str(self.user_id), text)

                await self.channel_layer.group_send(
                    self.group_name, {"type": "game_chat", "data": chat_obj}
                )

    async def game_chat(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    async def game_log(self, event):
        await self.send(text_data=json.dumps(event))

    async def game_move(self, event):
        await self.send(text_data=json.dumps({"type": "player_move", **event["data"]}))

    async def property_action(self, event):
        await self.send(text_data=json.dumps(event))

    async def your_turn(self, event):
        await self.send(text_data=json.dumps({"type": "turn_start", "message": "Ваш ход!"}))

    async def game_property_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
    
    async def game_balance_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "balance_update",
            "balances": event["balances"],
        }))