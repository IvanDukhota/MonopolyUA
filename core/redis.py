import redis
# from django.conf import settings

# pool = redis.ConnectionPool(
#     host=settings.REDIS["HOST"],
#     port=settings.REDIS["PORT"],
#     db=settings.REDIS["DB"],
#     password=settings.REDIS.get("PASSWORD", None),
#     decode_responses=True
# )

pool = redis.ConnectionPool(
    host="127.0.0.1",
    port=6379,
    db=2,
    password= None,
    decode_responses=True
)
client = redis.Redis(connection_pool=pool)
