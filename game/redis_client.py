import redis
import json
from core.redis import client
import time


def get_game_state(session_id: str) -> dict:
    state = {}

    meta_key = f"game:{session_id}:meta"
    state["meta"] = client.hgetall(meta_key)

    players_key = f"game:{session_id}:players"
    state["players"] = client.lrange(players_key, 0, -1)

    state["players_data"] = {}
    for user_id in state["players"]:
        player_key = f"game:{session_id}:player:{user_id}"
        state["players_data"][user_id] = client.hgetall(player_key)

    state["properties"] = {}

    property_list = client.keys(f"game:{session_id}:property:*")
    for prop_key in property_list:
        # prop_key == 'game:{session_id}:property:{property_id}'
        prop_id = prop_key.rsplit(":", 1)[1]
        state["properties"][prop_id] = client.hgetall(prop_key)

    logs_key = f"game:{session_id}:logs"
    state["logs"] = client.lrange(logs_key, 0, -1)

    chat_key = f"game:{session_id}:chat"
    state["chat"] = client.lrange(chat_key, 0, -1)

    return state


def append_chat_message(session_id: str, user_id: str, text: str) -> dict:
    key = f"game:{session_id}:chat"
    msg_obj = {
        "type": "chat",
        "user_id": user_id,
        "text": text,
        "timestamp": int(time.time()),
    }
    client.rpush(key, json.dumps(msg_obj))

    player_key = f"game:{session_id}:player:{user_id}"
    player_data = client.hgetall(player_key)

    msg_obj["username"] = player_data.get("username", "")
    msg_obj["color"] = player_data.get("color", "")

    # client.ltrim(key, -100, -1)
    return msg_obj


def create_game_log(session_id: str, message: str) -> dict:
    log_key = f"game:{session_id}:logs"
    timestamp = int(time.time())
    entry = {"action": "log", "message": message, "timestamp": timestamp}
    client.rpush(log_key, json.dumps(entry, ensure_ascii=False))
    return entry


def process_player_move(session_id: str, user_id: str, die1: int, die2: int) -> dict:
    meta_key = f"game:{session_id}:meta"
    player_key = f"game:{session_id}:player:{user_id}"
    property = f"game:{session_id}:property"

    current_turn = client.hget(meta_key, "current_turn")
    if str(user_id) != current_turn:
        raise ValueError("Не ваш ход")

    old_pos = int(client.hget(player_key, "position"))
    total = int(die1) + int(die2)
    new_pos = (old_pos + total) % 40

    client.hset(
        player_key, mapping={"position": new_pos, "last_roll": json.dumps([die1, die2])}
    )

    turn_order = json.loads(client.hget(meta_key, "turn_order"))
    idx = turn_order.index(str(user_id))
    next_turn = turn_order[(idx + 1) % len(turn_order)]
    client.hset(meta_key, "current_turn", next_turn)

    username = client.hget(player_key, "username") or user_id
    color = client.hget(player_key, "color")

    cell_name = client.hget(f"{property}:{new_pos}", "name")

    log_message = (
        f"{username} бросил {die1} и {die2}, "
        f"переместился с клетки {old_pos} на клетку {new_pos} ({cell_name})."
    )

    log_entry = create_game_log(session_id, log_message)

    return {
        "type": "player_move",
        "user_id": str(user_id),
        "from": old_pos,
        "to": new_pos,
        "color": color,
        "log": log_entry,
    }


def buy_property(
    session_id: str, user_id: str, property_id: str, property_name: str
) -> dict:

    player_key = f"game:{session_id}:player:{user_id}"
    prop_key = f"game:{session_id}:property:{property_id}"

    owner = client.hget(prop_key, "owner")
    if owner:
        raise ValueError("Уже куплено")

    price = int(client.hget(prop_key, "buy_price"))

    balance = int(client.hget(player_key, "balance"))
    if balance < price:
        raise ValueError("Недостаточно средств")

    client.hincrby(player_key, "balance", -price)

    client.hset(prop_key, "owner", str(user_id))

    username = client.hget(player_key, "username") or user_id
    color = client.hget(player_key, "color") or ""

    message = (
        f"{username} купил собственность {property_id} {property_name} за ${price}."
    )

    log_entry = create_game_log(session_id, message)

    return {
        "type": "property_bought",
        "property_id": property_id,
        "new_owner": str(user_id),
        "price": price,
        "new_balance": balance - price,
        "color": color,
        "log": log_entry,
    }


def pay_rent(session_id: str, payer_id: str, owner_id: str, amount: int) -> dict:
    payer_key = f"game:{session_id}:player:{payer_id}"
    owner_key = f"game:{session_id}:player:{owner_id}"

    client.hincrby(payer_key, "balance", -amount)
    client.hincrby(owner_key, "balance", amount)

    payer_balance = int(client.hget(payer_key, "balance"))
    owner_balance = int(client.hget(owner_key, "balance"))

    username = client.hget(payer_key, "username") or payer_id
    owner_name = client.hget(owner_key, "username") or owner_id
    message = f"{username} заплатил аренду ${amount} игроку {owner_name}."
    log_entry = create_game_log(session_id, message)

    return {
        "payer_id": payer_id,
        "owner_id": owner_id,
        "amount": amount,
        "payer_balance": payer_balance,
        "owner_balance": owner_balance,
        "log": log_entry,
    }

def process_utility_payment(session_id: str, payer_id: str, owner_id: str, amount: int, sum:int, multiplie:int) -> dict:
    payer_key = f"game:{session_id}:player:{payer_id}"
    owner_key = f"game:{session_id}:player:{owner_id}"

    payer_balance = int(client.hget(payer_key, "balance"))
    if payer_balance < amount:
        raise ValueError("Недостаточно средств для оплаты utility")

    new_payer_bal = client.hincrby(payer_key, "balance", -amount)
    new_owner_bal = client.hincrby(owner_key, "balance", amount)

    balances = {
        payer_id: new_payer_bal,
        owner_id: new_owner_bal,
    }

    payer_name = client.hget(payer_key, "username") or payer_id
    owner_name = client.hget(owner_key, "username") or owner_id
    message = (
        f"{payer_name} заплатил аренду ({sum}×{multiplie}) {amount}$ игроку {owner_name}."
    )
    log_entry = create_game_log(session_id, message)

    return {
        "balances": balances,
        "log": log_entry,
    }


def get_next_turn_and_log(session_id: str) -> dict:
    meta_key = f"game:{session_id}:meta"

    next_turn = client.hget(meta_key, "current_turn")
    if not next_turn:
        raise ValueError("Не удалось определить next_turn")

    player_key = f"game:{session_id}:player:{next_turn}"
    username = client.hget(player_key, "username") or next_turn

    message = f"Сейчас ходит {username}."
    log_entry = create_game_log(session_id, message)

    return {"next_turn": next_turn, "log": log_entry}
