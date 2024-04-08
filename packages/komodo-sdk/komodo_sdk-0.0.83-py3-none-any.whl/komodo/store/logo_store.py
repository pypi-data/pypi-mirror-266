import os
from io import BytesIO
from komodo.store.redis_database import RedisDatabase, get_redis_server

class LogoStore:
    def __init__(self, database=RedisDatabase.FILES):
        self.redis = get_redis_server(database)

    def upload_logo(self, logo_bytes, logo_extension, logo_id="default"):
        key = f"logo:{logo_id}"  
        self.redis.set(f"{key}:data", logo_bytes)
        self.redis.set(f"{key}:extension", logo_extension)

    def retrieve_logo(self, logo_id="default"):
        key = f"logo:{logo_id}"
        logo_bytes = self.redis.get(f"{key}:data")
        logo_extension = self.redis.get(f"{key}:extension")
        if logo_bytes and logo_extension:
            return logo_bytes, logo_extension.decode() 
        else:
            return None, None
