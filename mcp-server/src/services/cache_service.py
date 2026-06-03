import redis
import json
import logging
from functools import wraps
from typing import Optional, Any
from src.database.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis.ping()
            self.enabled = True
            logger.info("Connected to Redis for caching")
        except Exception as e:
            logger.warning(f"Redis connection failed, caching disabled: {e}")
            self.enabled = False

    def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Error reading from cache: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        if not self.enabled:
            return
        try:
            self.redis.set(key, json.dumps(value), ex=ttl)
        except Exception as e:
            logger.error(f"Error writing to cache: {e}")

cache_service = CacheService()

def mcp_cache(ttl: int = 3600):
    """
    Decorator to cache MCP tool results.
    Key format: tool_name:arg1:arg2...
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not cache_service.enabled:
                return f(*args, **kwargs)

            # Create a unique key based on function name and arguments
            # Sorted kwargs for consistency
            sorted_kwargs = sorted(kwargs.items())
            key_parts = [f.__name__] + [str(arg) for arg in args] + [f"{k}={v}" for k, v in sorted_kwargs]
            cache_key = ":".join(key_parts)

            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result:
                logger.info(f"Cache HIT for key: {cache_key}")
                # Add flag for telemetry without polluting Redis (fresh object from get)
                if isinstance(cached_result, dict):
                    cached_result["_cache_hit"] = True
                return cached_result

            # Execute function
            result = f(*args, **kwargs)
            
            # Store in cache FIRST (without the telemetry flag)
            cache_service.set(cache_key, result, ttl=ttl)
            
            # Add flag for telemetry (if it's a dict)
            if isinstance(result, dict):
                result["_cache_hit"] = False
                
            return result
        return wrapper
    return decorator
