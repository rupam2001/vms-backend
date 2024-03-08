import redis
from django.conf import settings
redis_store = redis.StrictRedis(
        host='192.168.1.8',
        port=6379,
        password='foobared123',
        decode_responses=True,
    )


redis_store.ping()