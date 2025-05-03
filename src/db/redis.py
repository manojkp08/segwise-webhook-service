import redis
from src.app.config import settings

redis_client = redis.Redis.from_url(settings.REDIS_URL)

def get_redis():
    return redis_client