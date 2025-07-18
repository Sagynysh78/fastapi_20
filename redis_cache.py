import json
from typing import Optional, Any
import redis.asyncio as redis
from fastapi import Depends
from settings import settings

REDIS_URL = settings.redis_url
CACHE_TTL = settings.cache_ttl

# Global Redis connection
redis_client: Optional[redis.Redis] = None

async def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

async def close_redis_client():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()

class CacheManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Error getting from cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting from cache: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> bool:
        """Delete all keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            print(f"Error deleting pattern from cache: {e}")
            return False

def get_cache_manager(redis_client: redis.Redis = Depends(get_redis_client)) -> CacheManager:
    """Dependency to get cache manager"""
    return CacheManager(redis_client) 