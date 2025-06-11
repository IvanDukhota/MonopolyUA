import json
import asyncio
import random
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from .redis_client import (
    client,
    get_game_state,
    append_chat_message,
    process_player_move,
    create_game_log,
    buy_property,
    pay_rent,
    process_utility_payment,
    build_house,
    sell_house,
    mortgage_property,
    redeem_property,
    init_roll_dice_turn,
    pass_turn_to_next,
    pay_debt
)

MOVE_CARDS = [
    {
        "code": "get_out_of_jail",
        "title": "Картка «Звільнення з в'язниці»",
        "description": "При попаданні у в'язницю ви одразу ж звільняєтеся."
    },
]

MONEY_CARDS = [
    {
        "code": "birthday_bonus",
        "title": "День народження",
        "description": "Банк виплачує вам $1000 у подарунок."
    },
]


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

        turn_state_key = f"game:{self.session_id}:turn_state"
        turn_state = client.hgetall(turn_state_key) or {}
        current_phase = turn_state.get("phase")

        current_turn = state["meta"].get("current_turn")

        if current_phase == "new_game" and str(self.user_id) == current_turn:
            new_turn_state = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: init_roll_dice_turn(self.session_id, self.user_id, timeout_seconds=15)
            )

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "turn_state_update",
                    "turn_state": new_turn_state
                }
            )

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
                player_key = f"game:{self.session_id}:player:{self.user_id}"
                pdata = client.hgetall(player_key)
                in_jail = int(pdata.get("in_jail", 0))
                jail_left = int(pdata.get("jail_turns_left", 0))

                if in_jail and jail_left > 0:
                    username = pdata.get("username") or str(self.user_id)
                    new_left = jail_left - 1
                    
                    if new_left > 1:
                        client.hset(player_key, "jail_turns_left", new_left)
                        log_text = (
                            f"{username} пропускає хід, оскільки перебуває у в'язниці, "
                            f"залишилося пропустити {new_left} хід(ів)."
                        )
                        msg_text = (
                            f"Ви пропускаєте хід, оскільки перебуває у в'язниці,"
                            f"залишилося пропустити {new_left} хід(ів)."
                        )

                    else:
                        client.hset(player_key, mapping={
                            "jail_turns_left": 0,
                            "in_jail": 0,
                        })
                        log_text = (
                            f"{username} пропускає хід, оскільки перебуває у в'язниці, "
                            "але виходить і наступного разу зможе ходити."
                        )
                        msg_text = (
                            f"Ви пропускаєте хід, оскільки перебуває у в'язниці, "
                            "але виходьте і наступного разу зможете ходити."
                        )

                    log = create_game_log(self.session_id, log_text)

                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": log["message"]},
                    )

                    await self.channel_layer.group_send(
                        f"user_{self.user_id}",
                        {"type": "message", "message": msg_text},
                    )

                    await pass_turn_to_next(self.session_id)
                    return


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

                prop = client.hgetall(prop_key)
                ptype = prop.get("type")
                owner_id = prop.get("owner")

                turn_state_key = f"game:{self.session_id}:turn_state"

                if ptype in ("company", "automaker", "utility") and owner_id and owner_id != result["user_id"]:
                    owner_key = f"game:{self.session_id}:player:{owner_id}"
                    owner_name = client.hget(owner_key, "username") or owner_id

                    if prop.get("mortgaged") == "1":
                        username = client.hget(f"game:{self.session_id}:player:{self.user_id}", "username") or str(self.user_id)
                        prop_name = prop.get("name", "")
                        log_msg = (
                            f"{username} попал на «{prop_name}», "
                            "але вона під заставою — орендну плату не стягуємо."
                        )
                        log_entry = create_game_log(self.session_id, log_msg)
                        await self.channel_layer.group_send(
                            self.group_name,
                            {"type": "game_log", "message": log_entry["message"]},
                        )

                        await pass_turn_to_next(self.session_id)
                        return

                    if ptype == "company":
                        rents  = json.loads(prop["rent"])
                        houses = int(prop.get("houses", 0))
                        amount = rents[houses]

                    elif ptype == "automaker":
                        automaker_keys = client.keys(f"game:{self.session_id}:property:*")
                        count = 0
                        for key in automaker_keys:
                            p = client.hgetall(key)
                            if p.get("type") == "automaker" and p.get("owner") == owner_id:
                                count += 1
                        rents = json.loads(prop["rent"])
                        amount = rents[count - 1] if 1 <= count <= len(rents) else rents[-1]

                    elif ptype == "utility":
                        util_keys = client.keys(f"game:{self.session_id}:property:*")
                        util_count = 0
                        for key in util_keys:
                            p = client.hgetall(key)
                            if p.get("type") == "utility" and p.get("owner") == owner_id:
                                util_count += 1
                        multiplier = 4 if util_count == 1 else 10

                        expires_at = int(time.time()) + 35
                        client.hset(turn_state_key, mapping={
                            "phase": "await_pay_utility",
                            "current_player": str(self.user_id),
                            "expires_at": str(expires_at),

                            "action_payload": json.dumps({
                                "property_id": result["to"],
                                "owner": owner_id,
                                "owner_name": owner_name,
                                "multiplier": multiplier,
                            }),
                        })

                        new_state = client.hgetall(turn_state_key)
                        await self.channel_layer.group_send(
                            self.group_name,
                            {"type": "turn_state_update", "turn_state": new_state},
                        )
                        return

                    expires_at = int(time.time()) + 35
                    client.hset(turn_state_key, mapping={
                        "phase": "await_pay_rent",
                        "current_player": str(self.user_id),
                        "expires_at": str(expires_at),
                        "action_payload": json.dumps({
                            "property_id": result["to"],
                            "owner": owner_id,
                            "owner_name": owner_name,
                            "amount": amount
                        }),
                    })
                    new_state = client.hgetall(turn_state_key)
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "turn_state_update", "turn_state": new_state},
                    )
                    return

                elif ptype in ("company", "automaker", "utility") and not owner_id:
                    price = int(prop["buy_price"])
                    expires_at = int(time.time()) + 35
                    client.hset(turn_state_key, mapping={
                        "phase": "await_purchase",
                        "current_player": str(self.user_id),
                        "expires_at": str(expires_at),
                        "action_payload": json.dumps({
                            "property_id": result["to"],
                            "property_name": prop.get("name",""),
                            "price": price
                        }),
                    })
                    new_state = client.hgetall(turn_state_key)
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "turn_state_update", "turn_state": new_state},
                    )
                    return

                elif ptype in ("company", "automaker", "utility") and owner_id == result["user_id"]:
                    await pass_turn_to_next(self.session_id)
                    return

                elif ptype == "action":
                    action_type = prop.get("action_type")
                    player_key = f"game:{self.session_id}:player:{self.user_id}"
                    username = client.hget(player_key, "username") or str(self.user_id)

                    if action_type == "move":
                        card = random.choice(MOVE_CARDS)
                    elif action_type == "money":
                        card = random.choice(MONEY_CARDS)
                    else:
                        return

                    log_text = f"{username} вытянул «{card['title']}»: {card['description']}"
                    log_entry = create_game_log(self.session_id, log_text)

                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": log_entry["message"]},
                    )

                    await self.channel_layer.group_send(
                        f"user_{self.user_id}",
                        {"type": "message", "message": card["description"]},
                    )

                    if card["code"] == "get_out_of_jail":
                        client.hset(player_key, "immune_to_jail", 1)

                    elif card["code"] == "birthday_bonus":
                        client.hincrby(player_key, "balance", 1000)
                        new_balance = int(client.hget(player_key, "balance"))
                        await self.channel_layer.group_send(
                            self.group_name,
                            {
                                "type": "game_balance_update",
                                "balances": { str(self.user_id): new_balance },
                            },
                        )            

                    await pass_turn_to_next(self.session_id)
                    return

                elif ptype == "side":
                    cell_name = prop.get("name", "")
                    player_key = f"game:{self.session_id}:player:{self.user_id}"
                    username = client.hget(player_key, "username") or self.user_id

                    if cell_name in ("Start", "Prison/Pass", "Casino"):

                        await pass_turn_to_next(self.session_id)

                    
                    elif cell_name == "GoToPrison":
                        immune = int(client.hget(player_key, "immune_to_jail") or 0)

                        async def delayed_prison_actions():
                            await asyncio.sleep(2)

                            await self.channel_layer.group_send(
                                self.group_name,
                                {
                                    "type": "game_move",
                                    "data": {
                                        "user_id": str(self.user_id),
                                        "from": result["to"],
                                        "to": 10,
                                        "color": result["color"],
                                    },
                                },
                            )
                            client.hset(
                                player_key, 
                                mapping={
                                    "position": 10,
                                }
                            )

                            if immune:
                                client.hset(player_key, "immune_to_jail", 0)
                                msg_all = (
                                    f"{username} потрапив на GoToPrison, "
                                    "але використав карту «Вихід із в'язниці» і одразу ж звільнився."
                                )

                                log_entry = create_game_log(self.session_id, msg_all)
                                await self.channel_layer.group_send(
                                    self.group_name,
                                    {"type": "game_log", "message": log_entry["message"]},
                                )

                                msg_self = (
                                    "Ви потрапили на клітку GoToPrison, "
                                    "але завдяки карті «Вихід із в'язниці» відразу ж вільні."
                                )
                                await self.channel_layer.group_send(
                                    f"user_{self.user_id}",
                                    {"type": "message", "message": msg_self},
                                )

                            else:
                                client.hset(player_key, mapping={
                                    "in_jail": 1,
                                    "jail_turns_left": 3,
                                })

                                msg_all = f"{username} відправлений у в'язницю та пропустить 3 ходи."

                                log_entry = create_game_log(self.session_id, msg_all)
                                await self.channel_layer.group_send(
                                    self.group_name,
                                    {"type": "game_log", "message": log_entry["message"]},
                                )

                                msg_self = "Ви потрапили на клітку GoToPrison і відправлені у в'язницю! Вам доведеться пропустити 3 ходи."
                                await self.channel_layer.group_send(
                                    f"user_{self.user_id}",
                                    {"type": "message", "message": msg_self},
                                )

                            await pass_turn_to_next(self.session_id)

                        asyncio.create_task(delayed_prison_actions())
                        return

            elif msg.get("type") == "confirm_buy":
                property_id = msg.get("property_id")
                property_name = msg.get("property_name")
                try:
                    update = buy_property(self.session_id, self.user_id, property_id, property_name)
                except ValueError as e:
                    msg_self = str(e)
                    await self.channel_layer.group_send(
                        f"user_{self.user_id}",
                        {"type": "message", "message": msg_self}
                    )
                    username = client.hget(f"game:{self.session_id}:player:{self.user_id}", "username") or str(self.user_id)
                    log_msg = f"{username} не зміг купити власність {property_id} «{property_name}» через нестачу коштів."
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": log_msg}
                    )
                    await pass_turn_to_next(self.session_id)
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

                await pass_turn_to_next(self.session_id)

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

                await pass_turn_to_next(self.session_id)


            elif msg.get("type") == "confirm_pay_rent":
                owner   = msg["owner"]
                amount  = int(msg["amount"])
                payer = str(self.user_id)

                result = pay_rent(self.session_id, payer, owner, amount)
                action = result.get("action")

                if action == "normal":
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            "type": "game_balance_update",
                            "balances": result["balances"],
                        }
                    )
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": result["log"]["message"]}
                    )

                    await pass_turn_to_next(self.session_id)

                elif action == "liquidate":
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": result["log"]["message"]}
                    )
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            "type": "turn_state_update",
                            "turn_state": result["turn_state"]
                        }
                    )

                elif action == "bankrupt":
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": result["log"]["message"]}
                    )
                     # 2) Log returned properties
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": result["return_log"]["message"]}
                    )
                    # 3) Inform all clients to clear bankrupt player's state
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            "type": "player_bankrupt",
                            "player_id": self.user_id,
                            "returned_properties": result["returned_properties"]
                        }
                    )
                    # 4) Personal message to bankrupt player
                    msg_self = (
                        f"Вы обанкротились и заняли {result['place']}-е место из {result['total_players']}."
                    )
                    await self.channel_layer.group_send(
                        f"user_{self.user_id}",
                        {"type": "message", "message": msg_self},
                    )
                    # 5) Move to next turn
                    await pass_turn_to_next(self.session_id)

                elif action == "game_over":
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": result["log"]["message"]}
                    )
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "turn_state_update", "turn_state": result["turn_state"]}
                    )


            if msg.get("type") == "confirm_pay_utility":
                payer = str(self.user_id)
                owner = msg["owner"]
                dice = msg["dice"]
                multiplier = int(msg["multiplier"])         
                dice_sum = sum(dice or [])

                result = process_utility_payment(self.session_id, payer, owner, dice_sum, multiplier)
                action = result.get("action")

                if action == "normal":
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
                        {"type": "game_log", "message": log_entry["message"]}
                    )
                    await pass_turn_to_next(self.session_id)

                elif result.get("action") == "liquidate":
                    log_entry = result["log"]
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": log_entry["message"]}
                    )

                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            "type": "turn_state_update",
                            "turn_state": result["turn_state"]
                        }
                    )

                elif action == "bankrupt":
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": result["log"]["message"]}
                    )
                     # 2) Log returned properties
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": result["return_log"]["message"]}
                    )
                    # 3) Inform all clients to clear bankrupt player's state
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            "type": "player_bankrupt",
                            "player_id": self.user_id,
                            "returned_properties": result["returned_properties"]
                        }
                    )
                    # 4) Personal message to bankrupt player
                    msg_self = (
                        f"Ви збанкрутували і зайняли {result['place']}-е місце з {result['total_players']}."
                    )
                    await self.channel_layer.group_send(
                        f"user_{self.user_id}",
                        {"type": "message", "message": msg_self},
                    )
                    # 5) Move to next turn
                    await pass_turn_to_next(self.session_id)

                elif action == "game_over":
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": result["log"]["message"]}
                    )
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "turn_state_update", "turn_state": result["turn_state"]}
                    )


            elif msg.get("type") == "confirm_pay_debt":
                payer = str(self.user_id)
                creditor = msg["creditor"]
                amount = int(msg["amount"])

                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: pay_debt(self.session_id, payer, creditor, amount)
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
                await pass_turn_to_next(self.session_id)


            elif msg.get("type") == "build_house":
                property_id = msg.get("property_id")
                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: build_house(self.session_id, self.user_id, property_id)
                    )
                except ValueError as e:
                    msg_self = str(e)
                    await self.channel_layer.group_send(
                        f"user_{self.user_id}",
                        {"type": "message", "message": msg_self}
                    )
                    username = client.hget(f"game:{self.session_id}:player:{self.user_id}", "username") or str(self.user_id)
                    log_msg = f"{username} не зміг побудувати на {property_id} — нестача коштів."
                    await self.channel_layer.group_send(
                        self.group_name,
                        {"type": "game_log", "message": log_msg}
                    )
                    await pass_turn_to_next(self.session_id)
                    return

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "build_house",
                        "property_id": result["property_id"],
                        "houses": result["new_houses"],
                        "owner_id": result["owner_id"],
                    },
                )

                log_entry = result["log"]
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": log_entry["message"],
                    },
                )

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_balance_update",
                        "balances": {
                            result["owner_id"]: result["new_balance"]
                        },
                    },
                )

                return

            elif msg.get("type") == "sell_house":
                property_id = msg.get("property_id")
                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: sell_house(self.session_id, self.user_id, property_id)
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
                        "type": "sell_house",
                        "property_id": result["property_id"],
                        "houses": result["new_houses"],
                        "owner_id": result["owner_id"],
                    },
                )

                log_entry = result["log"]
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": log_entry["message"],
                    },
                )

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_balance_update",
                        "balances": {
                            result["owner_id"]: result["new_balance"]
                        },
                    },
                )

                return

            elif msg.get("type") == "mortgage_property":
                property_id = msg.get("property_id")
                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: mortgage_property(self.session_id, self.user_id, property_id)
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
                        "type": "property_mortgaged",
                        "property_id": result["property_id"],
                        "mortgaged": result["new_mortgaged"],
                        "owner_id": result["owner_id"],
                        "mortgage_turns_left": result["mortgage_turns_left"],
                        "color": result["color"],
                    },
                )

                log_entry = result["log"]
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": log_entry["message"],
                    },
                )

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_balance_update",
                        "balances": {
                            result["owner_id"]: result["new_balance"]
                        },
                    },
                )

                return
            
            elif msg.get("type") == "redeem_property":
                property_id = msg.get("property_id")
                try:
                    result = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: redeem_property(self.session_id, self.user_id, property_id)
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
                        "type": "property_redeemed",
                        "property_id": result["property_id"],
                        "mortgaged": result["new_mortgaged"],
                        "owner_id": result["owner_id"],
                        "mortgage_turns_left": result["mortgage_turns_left"]
                    },
                )

                log_entry = result["log"]
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_log",
                        "message": log_entry["message"],
                    },
                )

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        "type": "game_balance_update",
                        "balances": {
                            result["owner_id"]: result["new_balance"]
                        },
                    },
                )
                return
        
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

    async def game_log(self, event):
        await self.send(text_data=json.dumps(event))

    async def game_move(self, event):
        await self.send(text_data=json.dumps({"type": "player_move", **event["data"]}))

    async def game_property_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
    
    async def game_balance_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "balance_update",
            "balances": event["balances"],
        }))
    
    async def build_house(self, event):
        await self.send(text_data=json.dumps(event))

    async def sell_house(self, event):
        await self.send(text_data=json.dumps(event))

    async def property_mortgaged(self, event):
        await self.send(text_data=json.dumps(event))

    async def property_redeemed(self, event):
        await self.send(text_data=json.dumps(event))
    
    async def message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message": event.get("message", "")
        }))

    async def turn_state_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def mortgage_batch_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "mortgage_batch_update",
            "updates": event["updates"]
        }))

    async def property_released(self, event):
        await self.send(text_data=json.dumps({
            "type": "property_released",
            "property_id": event["property_id"]
        }))

    async def player_bankrupt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_bankrupt',
            'player_id': event['player_id'],
            'returned_properties': event['returned_properties'],
            'place': event.get('place'),
            'total_players': event.get('total_players')
        }))