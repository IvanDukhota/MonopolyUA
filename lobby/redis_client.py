import uuid
import json
from core.redis import client


def lobby_meta_key(lobby_id: str) -> str:
    return f"lobby:{lobby_id}:meta"

def lobby_players_key(lobby_id: str) -> str:
    return f"lobby:{lobby_id}:players"


def get_player_list(lobby_id):
    players = list(client.smembers(lobby_players_key(lobby_id)))
    return players


def list_lobbies() -> list[dict]:
    ids = client.smembers('lobbies:available')
    lobbies = []
    for lid in ids:
        meta = client.hgetall(lobby_meta_key(lid))
        if not meta:
            continue
        lobby = {
            'id': str(lid),
            'name': meta.get('name'),
            'region': meta.get('region'),
            'max_players': int(meta.get('max_players', 0)),
            'invite_only': bool(int(meta.get('invite_only', 0))),
            'creator': meta.get('creator'),
            'started': bool(int(meta.get('started', 0))),
            'created_at': meta.get('created_at'),
            'players_count': client.scard(lobby_players_key(lid)),
            'players': get_player_list(lid)
        }
        lobbies.append(lobby)
    return lobbies


def get_lobby_meta(lobby_id: str) -> dict:
    meta = client.hgetall(lobby_meta_key(lobby_id))
    if not meta:
        return {}
    return {
        'id': str(lobby_id),
        'name': meta.get('name'),
        'region': meta.get('region'),
        'max_players': int(meta.get('max_players', 0)),
        'invite_only': bool(int(meta.get('invite_only', 0))),
        'creator': meta.get('creator'),
        'started': bool(int(meta.get('started', 0))),
        'created_at': meta.get('created_at'),
        'players_count': client.scard(lobby_players_key(lobby_id)),
        'players': get_player_list(lobby_id)
    }


def new_lobby_id() -> str:
    return str(uuid.uuid4())

def create_lobby(meta: dict) -> None:
    client.hset(lobby_meta_key(meta['id']), mapping={
        'name': meta['name'],
        'region': meta['region'],
        'max_players': meta['max_players'],
        'invite_only': int(meta['invite_only']),
        'creator': meta['creator'],
        'started': int(meta['started']),
        'created_at': meta['created_at'],
    })

    client.sadd(lobby_players_key(meta['id']), meta['creator'])
    client.sadd('lobbies:available', meta['id'])

    meta['players_count'] = client.scard(lobby_players_key(meta['id']))
    meta['players'] = get_player_list(meta['id'])

    client.publish('lobbies:updates', json.dumps({'action':'create', 'lobby': meta}))

def remove_lobby(lobby_id: str) -> None:
    meta_key    = lobby_meta_key(lobby_id)
    players_key = lobby_players_key(lobby_id)
    players = get_player_list(lobby_id)

    client.srem('lobbies:available', lobby_id)
    client.delete(meta_key, players_key)

    client.publish('lobbies:updates', json.dumps({'action':'remove', 'id': lobby_id, 'players': players}))


def join_lobby(lobby_id: str, user_id: str) -> int:
    client.sadd(lobby_players_key(lobby_id), user_id)
    lobby = get_lobby_meta(lobby_id)

    update = {'action':'update', 'lobby': lobby}
    client.publish('lobbies:updates', json.dumps(update))
    return lobby['players_count']


def leave_lobby(lobby_id: str, user_id: str) -> int:
    client.srem(lobby_players_key(lobby_id), user_id)
    lobby = get_lobby_meta(lobby_id)

    update = {'action':'update', 'lobby': lobby}
    client.publish('lobbies:updates', json.dumps(update))
    return lobby['players_count']

def remove_player_from_lobby(lobby_id: str, user_id: str) -> int:
    key = lobby_players_key(lobby_id)
    client.srem(key, user_id)

    lobby = get_lobby_meta(lobby_id)

    update = {'action':'kick', 'lobby': lobby, 'remove_player': user_id}
    client.publish('lobbies:updates', json.dumps(update))
    return lobby['players_count']



