import uuid, json
from datetime import datetime
from core.redis import client
from django.contrib.auth import get_user_model

User = get_user_model()

# Ключи


def lobby_meta_key(lobby_id: str) -> str:
    return f"lobby:{lobby_id}:meta"


def lobby_players_key(lobby_id: str) -> str:
    return f"lobby:{lobby_id}:players"


def get_player_list(lobby_id):
    players = list(client.smembers(lobby_players_key(lobby_id)))
    return players


# Список доступных лобби
def list_lobbies() -> list[dict]:
    ids = client.smembers("lobbies:available")
    lobbies = []
    for lid in ids:
        meta = client.hgetall(lobby_meta_key(lid))
        if not meta:
            continue
        lobby = {
            "id": str(lid),
            "name": meta.get("name"),
            "region": meta.get("region"),
            "max_players": int(meta.get("max_players", 0)),
            "invite_only": bool(int(meta.get("invite_only", 0))),
            "creator": meta.get("creator"),
            "started": bool(int(meta.get("started", 0))),
            "created_at": meta.get("created_at"),
            "players_count": client.scard(lobby_players_key(lid)),
            "players": get_player_list(lid),
        }
        lobbies.append(lobby)
    return lobbies


# Метаданные одного лобби


def get_lobby_meta(lobby_id: str) -> dict:
    meta = client.hgetall(lobby_meta_key(lobby_id))
    if not meta:
        return {}
    return {
        "id": str(lobby_id),
        "name": meta.get("name"),
        "region": meta.get("region"),
        "max_players": int(meta.get("max_players", 0)),
        "invite_only": bool(int(meta.get("invite_only", 0))),
        "creator": meta.get("creator"),
        "started": bool(int(meta.get("started", 0))),
        "created_at": meta.get("created_at"),
        "players_count": client.scard(lobby_players_key(lobby_id)),
        "players": get_player_list(lobby_id),
    }


# Создание/удаление лобби


def new_lobby_id() -> str:
    return str(uuid.uuid4())


def create_lobby(meta: dict) -> None:
    client.hset(
        lobby_meta_key(meta["id"]),
        mapping={
            "name": meta["name"],
            "region": meta["region"],
            "max_players": meta["max_players"],
            "invite_only": int(meta["invite_only"]),
            "creator": meta["creator"],
            "started": int(meta["started"]),
            "created_at": meta["created_at"],
        },
    )

    client.sadd(lobby_players_key(meta["id"]), meta["creator"])
    client.sadd("lobbies:available", meta["id"])

    meta["players_count"] = client.scard(lobby_players_key(meta["id"]))
    meta["players"] = get_player_list(meta["id"])

    client.publish("lobbies:updates", json.dumps({"action": "create", "lobby": meta}))


def remove_lobby(lobby_id: str) -> None:
    meta_key = lobby_meta_key(lobby_id)
    players_key = lobby_players_key(lobby_id)
    players = get_player_list(lobby_id)

    client.srem("lobbies:available", lobby_id)
    client.delete(meta_key, players_key)

    client.publish(
        "lobbies:updates",
        json.dumps({"action": "remove", "id": lobby_id, "players": players}),
    )


# Присоединение/отсоединение игроков


def join_lobby(lobby_id: str, user_id: str) -> int:
    client.sadd(lobby_players_key(lobby_id), user_id)
    lobby = get_lobby_meta(lobby_id)

    update = {"action": "update", "lobby": lobby}
    client.publish("lobbies:updates", json.dumps(update))
    return lobby["players_count"]


def leave_lobby(lobby_id: str, user_id: str) -> int:
    client.srem(lobby_players_key(lobby_id), user_id)
    lobby = get_lobby_meta(lobby_id)

    update = {"action": "update", "lobby": lobby}
    client.publish("lobbies:updates", json.dumps(update))
    return lobby["players_count"]


def remove_player_from_lobby(lobby_id: str, user_id: str) -> int:
    key = lobby_players_key(lobby_id)
    client.srem(key, user_id)

    lobby = get_lobby_meta(lobby_id)

    update = {"action": "kick", "lobby": lobby, "remove_player": user_id}
    client.publish("lobbies:updates", json.dumps(update))
    return lobby["players_count"]


PROPERTY_DATA = {
    # light blue
    "1": {
        "name": "Discord",
        "type": "company",
        "buy_price": 60,
        "house_price": 50,
        "hotel_price": 50,
        "rent": [2, 10, 30, 90, 160, 250],
        "group": "light_blue",
    },  # :contentReference[oaicite:1]{index=1}
    "2": {
        "type": "action",
        "action_type": "move",
    },
    "3": {
        "name": "TeamSpeak",
        "type": "company",
        "buy_price": 60,
        "house_price": 50,
        "hotel_price": 50,
        "rent": [4, 20, 60, 180, 320, 450],
        "group": "light_blue",
    },  # :contentReference[oaicite:2]{index=2}
    "4": {
        "type": "action",
        "action_type": "money",
    },
    # Yellow
    "6": {
        "name": "Nike",
        "type": "company",
        "buy_price": 100,
        "house_price": 50,
        "hotel_price": 50,
        "rent": [6, 30, 90, 270, 400, 550],
        "group": "yellow",
    },  # :contentReference[oaicite:3]{index=3}
    "7": {
        "type": "action",
        "action_type": "move",
    },
    "8": {
        "name": "Adidas",
        "type": "company",
        "buy_price": 100,
        "house_price": 50,
        "hotel_price": 50,
        "rent": [6, 30, 90, 270, 400, 550],
        "group": "yellow",
    },  # :contentReference[oaicite:4]{index=4}
    "9": {
        "name": "Kappa",
        "type": "company",
        "buy_price": 120,
        "house_price": 50,
        "hotel_price": 50,
        "rent": [8, 40, 100, 300, 450, 600],
        "group": "yellow",
    },  # :contentReference[oaicite:5]{index=5}
    "10": {
        "name": "Prison/Pass",
        "type": "side",
    },
    # Green
    "11": {
        "name": "Visa",
        "type": "company",
        "buy_price": 140,
        "house_price": 100,
        "hotel_price": 100,
        "rent": [10, 50, 150, 450, 625, 750],
        "group": "green",
    },  # :contentReference[oaicite:6]{index=6}
    "13": {
        "name": "MasterCard",
        "type": "company",
        "buy_price": 140,
        "house_price": 100,
        "hotel_price": 100,
        "rent": [10, 50, 150, 450, 625, 750],
        "group": "green",
    },  # :contentReference[oaicite:7]{index=7}
    "14": {
        "name": "PayPal",
        "type": "company",
        "buy_price": 160,
        "house_price": 100,
        "hotel_price": 100,
        "rent": [12, 60, 180, 500, 700, 900],
        "group": "green",
    },  # :contentReference[oaicite:8]{index=8}
    # Orange
    "16": {
        "name": "Viber",
        "type": "company",
        "buy_price": 180,
        "house_price": 100,
        "hotel_price": 100,
        "rent": [14, 70, 200, 550, 750, 950],
        "group": "orange",
    },  # :contentReference[oaicite:9]{index=9}
    "17": {
        "type": "action",
        "action_type": "move",
    },
    "18": {
        "name": "WhatsApp",
        "type": "company",
        "buy_price": 180,
        "house_price": 100,
        "hotel_price": 100,
        "rent": [14, 70, 200, 550, 750, 950],
        "group": "orange",
    },  # :contentReference[oaicite:10]{index=10}
    "19": {
        "name": "Telegram",
        "type": "company",
        "buy_price": 200,
        "house_price": 100,
        "hotel_price": 100,
        "rent": [16, 80, 220, 600, 800, 1000],
        "group": "orange",
    },  # :contentReference[oaicite:11]{index=11}
    "20": {
        "name": "Casino",
        "type": "side",
    },
    # Brown
    "21": {
        "name": "Manchester United",
        "type": "company",
        "buy_price": 220,
        "house_price": 150,
        "hotel_price": 150,
        "rent": [18, 90, 250, 700, 875, 1050],
        "group": "brown",
    },  # :contentReference[oaicite:12]{index=12}
    "22": {
        "type": "action",
        "action_type": "move",
    },
    "23": {
        "name": "Real Madrid",
        "type": "company",
        "buy_price": 220,
        "house_price": 150,
        "hotel_price": 150,
        "rent": [18, 90, 250, 700, 875, 1050],
        "group": "brown",
    },  # :contentReference[oaicite:13]{index=13}
    "24": {
        "name": "Barcelona",
        "type": "company",
        "buy_price": 240,
        "house_price": 150,
        "hotel_price": 150,
        "rent": [20, 100, 300, 750, 925, 1100],
        "group": "brown",
    },  # :contentReference[oaicite:14]{index=14}
    # Pink
    "26": {
        "name": "McDonalds",
        "type": "company",
        "buy_price": 260,
        "house_price": 150,
        "hotel_price": 150,
        "rent": [22, 110, 330, 800, 975, 1150],
        "group": "pink",
    },  # :contentReference[oaicite:15]{index=15}
    "27": {
        "name": "Burger King",
        "type": "company",
        "buy_price": 260,
        "house_price": 150,
        "hotel_price": 150,
        "rent": [22, 110, 330, 800, 975, 1150],
        "group": "pink",
    },  # :contentReference[oaicite:16]{index=16}
    "29": {
        "name": "KFC",
        "type": "company",
        "buy_price": 280,
        "house_price": 150,
        "hotel_price": 150,
        "rent": [24, 120, 360, 850, 1025, 1200],
        "group": "pink",
    },  # :contentReference[oaicite:17]{index=17}
    "30": {
        "name": "GoToPrison",
        "type": "side",
    },
    # Purple
    "31": {
        "name": "AmericanAirlines",
        "type": "company",
        "buy_price": 300,
        "house_price": 200,
        "hotel_price": 200,
        "rent": [26, 130, 390, 900, 1100, 1275],
        "group": "purple",
    },  # :contentReference[oaicite:18]{index=18}
    "32": {
        "name": "Lufthansa",
        "type": "company",
        "buy_price": 300,
        "house_price": 200,
        "hotel_price": 200,
        "rent": [26, 130, 390, 900, 1100, 1275],
        "group": "purple",
    },  # :contentReference[oaicite:19]{index=19}
    "33": {
        "type": "action",
        "action_type": "move",
    },
    "34": {
        "name": "Emirates",
        "type": "company",
        "buy_price": 320,
        "house_price": 200,
        "hotel_price": 200,
        "rent": [28, 150, 450, 1000, 1200, 1400],
        "group": "purple",
    },  # :contentReference[oaicite:20]{index=20}
    "36": {
        "type": "action",
        "action_type": "money",
    },
    # Dark Blue
    "37": {
        "name": "Samsung",
        "type": "company",
        "buy_price": 350,
        "house_price": 200,
        "hotel_price": 200,
        "rent": [35, 175, 500, 1100, 1300, 1500],
        "group": "dark_blue",
    },  # :contentReference[oaicite:21]{index=21}
    "38": {
        "type": "action",
        "action_type": "move",
    },
    "39": {
        "name": "Apple",
        "type": "company",
        "buy_price": 400,
        "house_price": 200,
        "hotel_price": 200,
        "rent": [50, 200, 600, 1400, 1700, 2000],
        "group": "dark_blue",
    },  # :contentReference[oaicite:22]{index=22}

    "0": {
        "name": "Start",
        "type": "side",
    },

    # Automaker
    "5": {
        "name": "Audi",
        "type": "automaker",
        "buy_price": 200,
        "rent": [25, 50, 100, 200],
    },  # :contentReference[oaicite:23]{index=23}
    "15": {
        "name": "Mercedes",
        "type": "automaker",
        "buy_price": 200,
        "rent": [25, 50, 100, 200],
    },  # :contentReference[oaicite:24]{index=24}
    "25": {
        "name": "Ford",
        "type": "automaker",
        "buy_price": 200,
        "rent": [25, 50, 100, 200],
    },  # :contentReference[oaicite:25]{index=25}
    "35": {
        "name": "Ferrari",
        "type": "automaker",
        "buy_price": 200,
        "rent": [25, 50, 100, 200],
    },  # :contentReference[oaicite:26]{index=26}

    # Utilities
    "12": {
        "name": "Asus",
        "type": "utility",
        "buy_price": 150,
    },  # :contentReference[oaicite:27]{index=27}
    "28": {
        "name": "Logitech",
        "type": "utility",
        "buy_price": 150,
    },  # :contentReference[oaicite:28]{index=28}
}

PLAYER_COLORS = [
    "rgb(255, 165, 0)",
    "rgb(128, 0, 128)",
    "rgb(0, 128, 0)",
    "rgb(0, 0, 255)",
]


def start_lobby(lobby_id: str) -> str:
    lobby = get_lobby_meta(lobby_id)
    if not lobby:
        raise ValueError(f"Lobby {lobby_id} not found")
    players = lobby["players"]

    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    # 1. Активні сесії
    client.sadd("game:active", session_id)

    # 2. Метадані сесії
    meta_key = f"game:{session_id}:meta"
    client.hset(
        meta_key,
        mapping={
            "session_id": session_id,
            "current_turn": players[0],
            "turn_order": json.dumps(players),
            "created_at": now,
        },
    )

    # 3. Гравці в сесії
    players_key = f"game:{session_id}:players"
    for uid in players:
        client.rpush(players_key, uid)

    # 4. Ініціалізуємо дані гравців
    for idx, uid in enumerate(players):
        try:
            user = User.objects.get(pk=uid)
            username = user.username
            avatar_url = user.avatar.url if user.avatar else ""
        except User.DoesNotExist:
            username = ""
            avatar_url = ""

        color = PLAYER_COLORS[idx % len(PLAYER_COLORS)]
        player_key = f"game:{session_id}:player:{uid}"
        client.hset(
            player_key,
            mapping={
                "balance": 1500,
                "position": 0,
                "in_jail": 0,
                "jail_turns_left": 0,
                "debt_to_bank": json.dumps(
                    {"amount": 0, "interest_rate": 0, "turns_left": 0}
                ),
                "skip_turns": 0,
                "last_roll": json.dumps([0, 0]),
                "color": color,
                "username": username,
                "avatar": avatar_url,
            },
        )

    # 5. Ініціалізуємо кожну клітинку як хеш з PROPERTY_DATA
    for pid, data in PROPERTY_DATA.items():
        key = f"game:{session_id}:property:{pid}"

        mapping = {
            "type": data["type"],
            "owner": "",
        }

        if data["type"] == "company":
            mapping.update(
                {
                    "name": data["name"],
                    "buy_price": data["buy_price"],
                    "house_price": data["house_price"],
                    "hotel_price": data["hotel_price"],
                    "rent": json.dumps(data["rent"]),
                    "group": data["group"],
                    "houses": 0,
                    "mortgaged": 0,
                    "mortgage_turns_left": 0,
                    "skins": 0,
                }
            )

        elif data["type"] == "automaker":
            mapping.update(
                {
                    "name": data["name"],
                    "buy_price": data["buy_price"],
                    "rent": json.dumps(data["rent"]),
                }
            )

        elif data["type"] == "utility":
            mapping.update(
                {
                    "name": data["name"],
                    "buy_price": data["buy_price"],
                }
            )

        elif data["type"] == "action":
            mapping.update(
                {
                    "action_type": data.get("action_type"),
                }
            )

        elif data["type"] == "side":
            mapping.update(
                {
                    "name": data.get("name", ""),
                }
            )
        client.hset(key, mapping=mapping)

    # 6. Очищуємо логи та чат
    client.delete(f"game:{session_id}:logs", f"game:{session_id}:chat")

    # 7. Видаляємо лобі
    remove_lobby(lobby_id)

    # 8. Публікуємо старт гри
    client.publish(
        "lobbies:updates",
        json.dumps({"action": "start", "session_id": session_id, "players": players}),
    )

    return session_id
