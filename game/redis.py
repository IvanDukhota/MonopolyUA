import redis
import json

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=1, decode_responses=True)

def get_game_key(session_id, suffix):
    return f"game:{session_id}:{suffix}"

def save_player_state(session_id, nickname, state):
    key = get_game_key(session_id, f"board:{nickname}")
    redis_client.set(key, json.dumps(state))

def get_player_state(session_id, nickname):
    key = get_game_key(session_id, f"board:{nickname}")
    data = redis_client.get(key)
    return json.loads(data) if data else {}

def append_chat_message(session_id, message):
    key = get_game_key(session_id, "chat")
    redis_client.rpush(key, json.dumps(message))
    redis_client.ltrim(key, -50, -1)

def get_chat_messages(session_id):
    key = get_game_key(session_id, "chat")
    return [json.loads(m) for m in redis_client.lrange(key, 0, -1)]

def store_token_user(access_token, username):
    redis_client.set(f"token:{access_token}", username, ex=60*60)

def get_username_from_token(access_token):
    return redis_client.get(f"token:{access_token}")