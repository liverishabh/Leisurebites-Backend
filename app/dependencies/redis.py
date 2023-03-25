from redis import Redis

from app.config import config

redis_client = Redis(
    decode_responses=True,
    host=config.REDIS_SERVER,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    max_connections=200,
    retry_on_timeout=True,
    socket_timeout=300,
)
