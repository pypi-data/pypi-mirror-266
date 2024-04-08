import os
from enum import Enum

import redis


class RedisDatabase(Enum):
    DEFAULT = 0
    USERS = 1
    AGENTS = 2
    APPLIANCES = 3
    TOOLS = 4
    FILES = 5
    CONVERSATIONS = 6
    MESSAGES = 7
    COLLECTIONS = 8
    TEST = 9


LOCALHOST = 'localhost'

DEFAULT_REDIS_HOST = LOCALHOST
DEFAULT_REDIS_PORT = 6379


def get_redis_server(db: RedisDatabase = RedisDatabase.DEFAULT) -> redis.Redis:
    host = os.getenv('REDIS_HOST', DEFAULT_REDIS_HOST)
    port = os.getenv('REDIS_PORT', DEFAULT_REDIS_PORT)
    server = redis.Redis(host=host, port=port, db=db.value)
    if not server.ping():
        raise ValueError(f"Failed to connect to redis server: {host}:{port}")
    return server
