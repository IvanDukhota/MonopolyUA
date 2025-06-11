import redis
import json, time
from typing import Dict, Any
from core.redis import client
from channels.layers import get_channel_layer

CHANNEL_LAYER = get_channel_layer()


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

    turn_state_key = f"game:{session_id}:turn_state"
    raw_turn_state = client.hgetall(turn_state_key)

    state["turn_state"] = raw_turn_state or {}

    return state


def init_roll_dice_turn(
    session_id: str, user_id: str, timeout_seconds: int = 45
) -> dict:
    turn_state_key = f"game:{session_id}:turn_state"
    expires_at = int(time.time()) + timeout_seconds

    mapping = {
        "phase": "roll_dice",
        "current_player": str(user_id),
        "expires_at": str(expires_at),
        "action_payload": "",
    }

    client.hset(turn_state_key, mapping=mapping)
    raw = client.hgetall(turn_state_key)
    return raw


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

    username = client.hget(player_key, "username") or user_id
    color = client.hget(player_key, "color")

    cell_name = client.hget(f"{property}:{new_pos}", "name")

    log_message = (
        f"{username} кинув {die1} й {die2}, "
        f"перемістився з клітки {old_pos} на клітку {new_pos} ({cell_name})."
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
        raise ValueError("Недостатньо коштів")

    client.hincrby(player_key, "balance", -price)

    client.hset(prop_key, "owner", str(user_id))

    username = client.hget(player_key, "username") or user_id
    color = client.hget(player_key, "color") or ""

    message = (
        f"{username} купив власність {property_id} {property_name} за ${price}."
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
    
    payer_balance = int(client.hget(payer_key, "balance") or 0)

    payer_name = client.hget(payer_key, "username") or payer_id
    owner_name = client.hget(owner_key, "username") or owner_id
    
    
    if payer_balance >= amount:
        client.hincrby(payer_key, "balance", -amount)
        client.hincrby(owner_key, "balance", amount)

        new_payer_bal = int(client.hget(payer_key, "balance"))
        new_owner_bal = int(client.hget(owner_key, "balance"))

        balances = { payer_id: new_payer_bal, owner_id: new_owner_bal}

        message = f"{payer_name} заплатив оренду ${amount} гравцю {owner_name}."
        log_entry = create_game_log(session_id, message)

        return {"action": "normal", "balances": balances, "log": log_entry}
    
    total_assets = calculate_max_balance(session_id, payer_id)
    max_possible = payer_balance + total_assets

    if max_possible >= amount:
        log_msg = (
            f"{payer_name} не має достатньо готівки (${payer_balance}), "
            f"щоб сплатити оренду ${amount} гравцю {owner_name}. Початок продажу власності."
        )

        log_entry = create_game_log(session_id, log_msg)

        turn_state_key = f"game:{session_id}:turn_state"
        deadline = int(time.time()) + 180

        payload = {
                "currentCash": payer_balance,
                "totalOwed": amount,
                "totalAssets": total_assets,
                "creditorId": owner_id,
                "creditorName": owner_name,
            }
        
        mapping = {
                "phase": "await_pay_debt",
                "current_player": payer_id,
                "expires_at": str(deadline),
                "action_payload":  json.dumps(payload),
            }
        
        client.hset(turn_state_key, mapping=mapping)
        new_state = client.hgetall(turn_state_key)
        
        return {"action": "liquidate", "turn_state": new_state, "log": log_entry}
    
    reason = f"{payer_name} не зміг сплатити утиліту ${amount} та вичерпав усі можливі активи — банкрутство."
    log_entry = create_game_log(session_id, reason)

    result = process_bankruptcy(session_id, payer_id, payer_name)
    result["log"] = log_entry

    return result


def process_utility_payment(
    session_id: str, payer_id: str, owner_id: str, sum: int, multiplie: int
) -> dict:
    payer_key = f"game:{session_id}:player:{payer_id}"
    owner_key = f"game:{session_id}:player:{owner_id}"

    amount = sum * multiplie

    payer_balance = int(client.hget(payer_key, "balance") or 0)

    payer_name = client.hget(payer_key, "username") or payer_id
    owner_name = client.hget(owner_key, "username") or owner_id

    if payer_balance >= amount:
        new_payer_bal = client.hincrby(payer_key, "balance", -amount)
        new_owner_bal = client.hincrby(owner_key, "balance", amount)

        balances = {
            payer_id: new_payer_bal,
            owner_id: new_owner_bal,
        }

        message = f"{payer_name} заплатил утиліту ({sum}×{multiplie}) {amount}$ гравцю {owner_name}."
        log_entry = create_game_log(session_id, message)

        return {
            "action": "normal",
            "balances": balances,
            "log": log_entry,
        }
    
    total_assets = calculate_max_balance(session_id, payer_id)
    max_possible = payer_balance + total_assets

    if max_possible >= amount:

        log_msg = (
            f"{payer_name} не має достатньо готівки (${payer_balance}), "
            f"щоб сплатити утиліту ${amount} гравцю {owner_name}. Початок продажу власності."
        )
        log_entry = create_game_log(session_id, log_msg)

        turn_state_key = f"game:{session_id}:turn_state"
        deadline = int(time.time()) + 180

        payload = {
            "currentCash": payer_balance,
            "totalOwed": amount,
            "totalAssets": total_assets,
            "creditorId": owner_id,
            "creditorName": owner_name,
        }

        mapping = {
            "phase": "await_pay_debt",
            "current_player": payer_id,
            "expires_at": str(deadline),
            "action_payload": json.dumps(payload),
        }

        client.hset(turn_state_key, mapping=mapping)
        new_state = client.hgetall(turn_state_key)

        return {
            "action": "liquidate",
            "turn_state": new_state,
            "log": log_entry,
        }
    
    reason = f"{payer_name} не зміг сплатити утиліту ${amount} та вичерпав усі можливі активи — банкрутство."
    log_entry = create_game_log(session_id, reason)
    
    result = process_bankruptcy(session_id, payer_id, payer_name)
    result["log"] = log_entry

    return result
    

def pay_debt(session_id: str, payer_id: str, owner_id: str, amount: int) -> dict:
    payer_key = f"game:{session_id}:player:{payer_id}"
    owner_key = f"game:{session_id}:player:{owner_id}"

    payer_balance = int(client.hget(payer_key, "balance") or 0)

    payer_name = client.hget(payer_key, "username") or payer_id
    owner_name = client.hget(owner_key, "username") or owner_id

    if payer_balance < amount:
        raise ValueError("Недостатньо коштів для сплати боргу")

    client.hincrby(payer_key, "balance", -amount)
    client.hincrby(owner_key, "balance", amount)

    new_payer_bal = int(client.hget(payer_key, "balance") or 0)
    new_owner_bal = int(client.hget(owner_key, "balance") or 0)

    balances = {
        payer_id: new_payer_bal,
        owner_id: new_owner_bal,
    }

    message = f"{payer_name} заплатив оренду ${amount} гравцю {owner_name}."
    log_entry = create_game_log(session_id, message)

    return {
        "balances": balances,
        "log": log_entry,
    }


def calculate_max_balance(session_id: str, player_id: str) -> int:
    total_assets = 0

    property_keys = client.keys(f"game:{session_id}:property:*")
    for key in property_keys:

        prop = client.hgetall(key) or {}

        if prop.get("owner") != str(player_id):
            continue

        ptype = prop.get("type")
        if ptype == "company":
            houses = int(prop.get("houses", "0"))
            if houses > 0:
                house_price = int(prop.get("house_price", "0"))
                hotel_price = int(prop.get("hotel_price", "0"))

                if houses == 5:
                    total_assets += int(hotel_price * 0.5)
                    total_assets += 4 * int(house_price * 0.5)
                else:
                    total_assets += houses * int(house_price * 0.5)

            if prop.get("mortgaged", "0") == "0":
                buy_price = int(prop.get("buy_price", "0"))
                total_assets += int(buy_price * 0.8)

        elif ptype in ("automaker", "utility"):
            if prop.get("mortgaged", "0") == "0":
                buy_price = int(prop.get("buy_price", "0"))
                total_assets += int(buy_price * 0.8)

    return total_assets


def process_bankruptcy(session_id: str, player_id: str, payer_name: str) -> Dict[str, Any]:
    meta_key = f"game:{session_id}:meta"
    prop_keys = client.keys(f"game:{session_id}:property:*") or []
    player_key = f"game:{session_id}:player:{player_id}"
    
    returned = []
    details = []
    for prop_key in prop_keys:
        prop = client.hgetall(prop_key) or {}
        if prop.get("owner") == player_id:
            pid = prop_key.split(':')[-1]
            returned.append(pid)
            name = prop.get('name', '')
            details.append(f"{pid} - {name}")

            reset = {"owner": "", "mortgaged": "0", "mortgage_turns_left": "0"}
            if prop.get("type") == "company":
                reset["houses"] = "0"
            client.hset(prop_key, mapping=reset)


    turn_order = json.loads(client.hget(meta_key, "turn_order") or "[]")
    total_players = len(turn_order)

    place = total_players
    client.hset(player_key, "place", place)

    new_order = [pid for pid in turn_order if pid != player_id]
    client.hset(meta_key, "turn_order", json.dumps(new_order))

    if len(new_order) == 1:
        last_pid = new_order[0]
        client.hset(f"game:{session_id}:player:{last_pid}", "place", 1)

        players_list = client.lrange(f"game:{session_id}:players", 0, -1) or []
        rankings: Dict[str, str] = {}

        for pid in players_list:
            pid = pid.decode() if isinstance(pid, bytes) else pid
            raw_place = client.hget(f"game:{session_id}:player:{pid}", "place")
            p_place = raw_place.decode() if isinstance(raw_place, bytes) else raw_place
            rankings[p_place] = pid

        turn_state_key = f"game:{session_id}:turn_state"
        deadline = int(time.time()) + 300
        payload = {"rankings": rankings}
        mapping = {
            "phase": "game_over",
            "current_player": "",
            "expires_at": str(deadline),
            "action_payload": json.dumps(payload)
        }

        client.hset(turn_state_key, mapping=mapping)
        new_state = client.hgetall(turn_state_key)

        return {
            "action": "game_over",
            "turn_state": new_state
        }

    log_lines = [f'Вся власність {payer_name} перейшла банку:'] + details
    return_msg = "\n".join(log_lines)
    return_log = create_game_log(session_id, return_msg)

    return {
        "action": "bankrupt",
        "return_log": return_log,
        "returned_properties": returned,
        "place": place,
        "total_players": total_players
    }


def build_house(session_id: str, user_id: str, property_id: str) -> dict:
    """
    {
      "property_id": property_id,
      "new_houses": <int>,
      "house_price": <int>,
      "owner_id": str(user_id),
      "new_balance": <int>,
      "log": <entry from create_game_log>
    }
    """
    player_key = f"game:{session_id}:player:{user_id}"
    prop_key = f"game:{session_id}:property:{property_id}"

    property_name = client.hget(prop_key, "name")

    owner = client.hget(prop_key, "owner")
    if owner != str(user_id):
        raise ValueError("Ви не є власником цієї картки.")

    group = client.hget(prop_key, "group")
    if not group:
        raise ValueError("Не можна будувати на цій картці (не є company).")

    keys = client.keys(f"game:{session_id}:property:*")
    same_group_props = []
    for key in keys:
        p = client.hgetall(key)
        if p.get("type") == "company" and p.get("group") == group:
            same_group_props.append(p)

    for p in same_group_props:
        if p.get("owner") != str(user_id):
            raise ValueError(
                "У вас немає монополії: не всі картки групи належать вам."
            )

    existing_houses = int(client.hget(prop_key, "houses") or 0)
    if existing_houses >= 5:
        raise ValueError("Досягнуто максимум (вже стоїть готель).")

    house_price = int(client.hget(prop_key, "house_price") or 0)
    hotel_price = int(client.hget(prop_key, "hotel_price") or 0)
    if existing_houses < 4:
        price_to_pay = house_price
    else:
        price_to_pay = hotel_price

    balance = int(client.hget(player_key, "balance") or 0)
    if balance < price_to_pay:
        raise ValueError("Недостатньо коштів для придбання будинку/готелю.")

    new_balance = client.hincrby(player_key, "balance", -price_to_pay)

    new_houses = client.hincrby(prop_key, "houses", 1)

    username = client.hget(player_key, "username") or str(user_id)
    what_built = "отель" if new_houses == 5 else "дом"

    message = f"{username} побудував {what_built} на {property_id}: {property_name}."

    log_entry = create_game_log(session_id, message)

    raw_list = client.hget(player_key, "acted_props") or "[]"
    try:
        acted_list = json.loads(raw_list)
    except:
        acted_list = []
    if property_id not in acted_list:
        acted_list.append(property_id)
        client.hset(player_key, "acted_props", json.dumps(acted_list))

    return {
        "property_id": property_id,
        "new_houses": new_houses,
        "house_price": price_to_pay,
        "owner_id": str(user_id),
        "new_balance": new_balance,
        "log": log_entry,
    }


def sell_house(session_id: str, user_id: str, property_id: str) -> dict:
    """
    {
      "property_id": property_id,
      "new_houses": <int>,
      "refund_amount": <int>,
      "owner_id": str(user_id),
      "new_balance": <int>,
      "log": <entry from create_game_log>
    }
    """
    player_key = f"game:{session_id}:player:{user_id}"
    prop_key = f"game:{session_id}:property:{property_id}"

    property_name = client.hget(prop_key, "name")

    owner = client.hget(prop_key, "owner")
    if owner != str(user_id):
        raise ValueError("Ви не є власником цієї картки.")

    current_houses = int(client.hget(prop_key, "houses") or 0)
    if current_houses <= 0:
        raise ValueError("Немає будинків на продаж.")

    if current_houses == 5:
        refund_amount = int(client.hget(prop_key, "hotel_price") or 0)
    else:
        refund_amount = int(client.hget(prop_key, "house_price") or 0)

    new_balance = client.hincrby(player_key, "balance", refund_amount)

    new_houses = client.hincrby(prop_key, "houses", -1)

    username = client.hget(player_key, "username") or str(user_id)

    if current_houses == 5:
        what_sold = "готель"
    else:
        what_sold = "будинок"

    message = f"{username} продав {what_sold} на {property_id}:{property_name} і отримав {refund_amount}$. "
    log_entry = create_game_log(session_id, message)

    return {
        "property_id": property_id,
        "new_houses": new_houses,
        "refund_amount": refund_amount,
        "owner_id": str(user_id),
        "new_balance": new_balance,
        "log": log_entry,
    }


def mortgage_property(session_id: str, user_id: str, property_id: str) -> dict:
    """
    {
      "property_id": property_id,
      "new_mortgaged": "1",
      "owner_id": str(user_id),
      "new_balance": <int>,
      "log": <entry from create_game_log>
    }
    """

    player_key = f"game:{session_id}:player:{user_id}"
    prop_key = f"game:{session_id}:property:{property_id}"

    owner = client.hget(prop_key, "owner")
    if owner != str(user_id):
        raise ValueError("Ви не є власником цієї картки.")

    if client.hget(prop_key, "mortgaged") == "1":
        raise ValueError("Ця власність під заставою.")

    group = client.hget(prop_key, "group")
    if group:
        keys = client.keys(f"game:{session_id}:property:*")
        for key in keys:
            p = client.hgetall(key)
            if p.get("type") == "company" and p.get("group") == group:
                if int(p.get("houses", "0")) > 0:
                    raise ValueError(
                        "Не можна закласти, поки є будинки/готель у цій філії."
                    )

    client.hset(prop_key, "mortgaged", "1")
    client.hset(prop_key, "mortgage_turns_left", "5")

    buy_price = int(client.hget(prop_key, "buy_price") or 0)
    refund = int(buy_price * 0.8)
    new_balance = client.hincrby(player_key, "balance", refund)

    username = client.hget(player_key, "username") or str(user_id)
    color = client.hget(player_key, "color")

    property_name = client.hget(prop_key, "name")

    message = (
        f"{username} заклав власність {property_id}: {property_name} за {refund}$."
    )
    log_entry = create_game_log(session_id, message)

    return {
        "property_id": property_id,
        "new_mortgaged": "1",
        "mortgage_turns_left": "5",
        "owner_id": str(user_id),
        "new_balance": new_balance,
        "log": log_entry,
        "color": color,
    }


def redeem_property(session_id: str, user_id: str, property_id: str) -> dict:
    """
    {
      "property_id": <str>,
      "new_mortgaged": "0",
      "mortgage_turns_left": "0",
      "owner_id": <str>,
      "new_balance": <int>,
      "log": <log_entry>
    }
    """

    player_key = f"game:{session_id}:player:{user_id}"
    prop_key = f"game:{session_id}:property:{property_id}"

    owner = client.hget(prop_key, "owner")
    if owner != str(user_id):
        raise ValueError("Ви не є власником цієї картки.")

    if client.hget(prop_key, "mortgaged") != "1":
        raise ValueError("Ця власність не перебуває під заставою.")

    buy_price = int(client.hget(prop_key, "buy_price") or 0)
    cost = int(buy_price * 0.9)

    balance = int(client.hget(player_key, "balance") or "0")

    if balance < cost:
        raise ValueError("Недостатньо коштів на викуп з-під застави.")

    new_balance = client.hincrby(player_key, "balance", -cost)

    client.hset(prop_key, "mortgaged", "0")
    client.hset(prop_key, "mortgage_turns_left", "0")

    username = client.hget(player_key, "username") or str(user_id)
    property_name = client.hget(prop_key, "name")

    message = (
        f"{username} викупив власність {property_id}: {property_name} за {cost}$."
    )
    log_entry = create_game_log(session_id, message)

    raw_list = client.hget(player_key, "acted_props") or "[]"
    try:
        acted_list = json.loads(raw_list)
    except ValueError:
        acted_list = []
    if property_id not in acted_list:
        acted_list.append(property_id)
        client.hset(player_key, "acted_props", json.dumps(acted_list))

    return {
        "property_id": property_id,
        "new_mortgaged": "0",
        "mortgage_turns_left": "0",
        "owner_id": str(user_id),
        "new_balance": new_balance,
        "log": log_entry,
    }


async def pass_turn_to_next(session_id: str) -> None:
    meta_key = f"game:{session_id}:meta"
    turn_order = json.loads(client.hget(meta_key, "turn_order") or "[]")
    if not turn_order:
        raise ValueError("Turn order is empty")

    current_player = client.hget(meta_key, "current_turn")
    next_turn = None
        
    if current_player is None or current_player not in turn_order:
        players_key = f"game:{session_id}:players"
        raw = client.lrange(players_key, 0, -1) or []
        players_list = [pid.decode() if isinstance(pid, bytes) else pid for pid in raw]
        try:
            start_idx = players_list.index(current_player)
        except ValueError:
            raise ValueError(f"Current turn '{current_player}' not found in players list")
        n = len(players_list)
        for i in range(1, n):
            cand = players_list[(start_idx + i) % n]
            if cand in turn_order:
                next_turn = cand
                break
        if next_turn is None:
            raise ValueError("No active players to pass turn to")
        
    else:
        idx = turn_order.index(current_player)
        next_turn = turn_order[(idx + 1) % len(turn_order)]
    

    player_key_current = f"game:{session_id}:player:{current_player}"
    player_color = client.hget(player_key_current, "color") or ""
    player_username = client.hget(player_key_current, "username") or current_player

    batch_updates = []
    prop_keys = client.keys(f"game:{session_id}:property:*")

    for prop_key in prop_keys:
        prop = client.hgetall(prop_key)
        if not prop:
            continue

        owner = prop.get("owner")
        if owner != current_player:
            continue
        if prop.get("mortgaged") != "1":
            continue

        prop_id = prop_key.rsplit(":", 1)[1]
        old_left = int(prop.get("mortgage_turns_left", "0") or "0")

        if old_left > 1:
            new_left = old_left - 1
            client.hset(prop_key, mapping={"mortgage_turns_left": str(new_left)})

            batch_updates.append({
                "property_id": prop_id,
                "turns_left": str(new_left),
                "color": player_color,
            })

        else:
            client.hset(prop_key, mapping={
                "mortgaged": "0",
                "mortgage_turns_left": "0",
                "owner": ""
            })
            prop_name = prop.get("name", "")

            release_msg = (
                f"{player_username} не встиг викупити «{prop_name}» – "
                "власність повертається банку."
            )
            release_log = create_game_log(session_id, release_msg)
            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {"type": "game_log", "message": release_log["message"]}
            )

            await CHANNEL_LAYER.group_send(
                f"game_{session_id}",
                {
                    "type": "property_released",
                    "property_id": prop_id
                }
            )

    if batch_updates:
        await CHANNEL_LAYER.group_send(
            f"game_{session_id}",
            {
                "type": "mortgage_batch_update",
                "updates": batch_updates
            }
        )

    client.hset(player_key_current, "acted_props", json.dumps([]))

    client.hset(meta_key, "current_turn", next_turn)

    player_key_next = f"game:{session_id}:player:{next_turn}"
    username = client.hget(player_key_next, "username") or next_turn
    message = f"Сейчас ходит {username}."
    log_entry = create_game_log(session_id, message)

    turn_state_key = f"game:{session_id}:turn_state"

    new_ts = {
        "phase": "roll_dice",
        "current_player": str(next_turn),
        "expires_at": str(int(time.time()) + 55),
        "action_payload": ""
    }
    client.hset(turn_state_key, mapping=new_ts)

    await CHANNEL_LAYER.group_send(
        f"game_{session_id}",
        {
            "type": "turn_state_update",
            "turn_state": new_ts
        }
    )
    await CHANNEL_LAYER.group_send(
        f"game_{session_id}",
        {
            "type": "game_log",
            "message": log_entry["message"]
        }
    )