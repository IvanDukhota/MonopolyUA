import redis

pool = redis.ConnectionPool(
    host="127.0.0.1",
    port=6379,
    db=2,
    password= None,
    decode_responses=True
)
client = redis.Redis(connection_pool=pool)
