import asyncio
import time
import json
from channels.layers import get_channel_layer

from .redis_client import (
    client,
    pass_turn_to_next,
    create_game_log,
    pay_rent,
    process_utility_payment,
)

CHANNEL_LAYER = get_channel_layer()


async def monitor_all_games():
    """
    Фоновая корутина, которая каждую секунду прогоняет все активные сессии (game:active),
    смотрит, не истёк ли expires_at в turn_state, и если истёк — автоматически
    делает skip и передаёт ход дальше.
    """
    print("► monitor_all_games() запущен в фоновом loop’е")
    while True:
        await asyncio.sleep(1)
        active_sessions = client.smembers("game:active") or []
        now = int(time.time())

        for session_id in active_sessions:
            turn_state_key = f"game:{session_id}:turn_state"
            raw = client.hgetall(turn_state_key) or {}
            if not raw:
                continue

            phase = raw.get("phase")
            player = raw.get("current_player")
            expires_at = int(raw.get("expires_at", "0") or "0")

            if expires_at and now >= expires_at:
                state2 = client.hgetall(turn_state_key) or {}
                if state2.get("phase") == phase and state2.get("current_player") == player:

                    await handle_timeout_skip(session_id, player, phase, state2.get("action_payload"))


async def handle_timeout_skip(session_id: str, player_id: str, phase: str, action_payload: str):
    user_key = f"game:{session_id}:player:{player_id}"
    username = client.hget(user_key, "username") or player_id

    if phase == "await_purchase":
        payload = json.loads(action_payload or "{}")
        prop_id   = payload.get("property_id", "")
        prop_name = payload.get("property_name", "")
        decline_msg = (
            f"{username} не відповів вчасно – відхилено купівлю власності "
            f"{prop_id} «{prop_name}»."
        )
        log = create_game_log(session_id, decline_msg)
        await CHANNEL_LAYER.group_send(
            f"game_{session_id}",
            {"type": "game_log", "message": log["message"]}
        )
        await pass_turn_to_next(session_id)

    elif phase == "await_pay_rent":
        payload = json.loads(action_payload or "{}")
        owner  = payload.get("owner")
        amount = int(payload.get("amount", 0))
        payer  = player_id

        result = pay_rent(session_id, payer, owner, amount)
        action = result.get("action")

        if action == "normal":
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_balance_update", "balances": result["balances"]}
            )
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["log"]["message"]}
            )
            await pass_turn_to_next(session_id)

        elif action == "liquidate":
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["log"]["message"]}
            )
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "turn_state_update", "turn_state": result["turn_state"]}
            )

        elif action == "bankrupt":
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["log"]["message"]}
            )
             # 2) Log returned properties
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["return_log"]["message"]}
            )
            # 3) Inform all clients to clear bankrupt player's state
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {
                    "type": "player_bankrupt",
                    "player_id": player_id,
                    "returned_properties": result["returned_properties"]
                }
            )
            # 4) Personal message to bankrupt player
            msg_self = (
                f"Ви збанкрутували і зайняли {result['place']}-е місце з {result['total_players']}."
            )
            await CHANNEL_LAYER.group_send(
                f"user_{player_id}",
                {"type": "message", "message": msg_self},
            )
            # 5) Move to next turn
            await pass_turn_to_next(session_id)

        elif action == "game_over":
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["log"]["message"]}
            )
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "turn_state_update", "turn_state": result["turn_state"]}
            )

    elif phase == "await_pay_utility":
        payload = json.loads(action_payload or "{}")
        payer = player_id
        owner = payload.get("owner")
        dice_sum = int(payload.get("sum", 12))
        multiplier = int(payload.get("multiplier", 0))
        
        result = process_utility_payment(session_id, payer, owner, dice_sum, multiplier)
        action = result.get("action")

        if action == "normal":
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_balance_update", "balances": result["balances"]}
            )
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["log"]["message"]}
            )
            await pass_turn_to_next(session_id)

        elif action == "liquidate":
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["log"]["message"]}
            )
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "turn_state_update", "turn_state": result["turn_state"]}
            )

        elif action == "bankrupt":
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["log"]["message"]}
            )
             # 2) Log returned properties
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["return_log"]["message"]}
            )
            # 3) Inform all clients to clear bankrupt player's state
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {
                    "type": "player_bankrupt",
                    "player_id": player_id,
                    "returned_properties": result["returned_properties"]
                }
            )
            # 4) Personal message to bankrupt player
            msg_self = (
                f"Ви збанкрутували і зайняли {result['place']}-е місце з {result['total_players']}."
            )
            await CHANNEL_LAYER.group_send(
                f"user_{player_id}",
                {"type": "message", "message": msg_self},
            )
            # 5) Move to next turn
            await pass_turn_to_next(session_id)

        elif action == "game_over":
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": result["log"]["message"]}
            )
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "turn_state_update", "turn_state": result["turn_state"]}
            )


    elif phase == "roll_dice":
        skip_msg = f"Игрок {username} не встиг кинути кубики і пропускає хід."
        skip_log = create_game_log(session_id, skip_msg)
        await CHANNEL_LAYER.group_send(
            f"game_{session_id}",
            {"type": "game_log", "message": skip_log["message"]}
        )
        await pass_turn_to_next(session_id)

    elif phase != "game_over":
        generic_msg = f"{username} не відповів вчасно на дію «{phase}» — пропускає хід."
        generic_log = create_game_log(session_id, generic_msg)
        await CHANNEL_LAYER.group_send(
            f"game_{session_id}",
            {"type": "game_log", "message": generic_log["message"]}
        )
