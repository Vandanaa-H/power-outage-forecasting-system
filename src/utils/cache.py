import asyncio
import aioredis
from typing import Any, Optional, Dict
import json
import logging
from datetime import datetime, timedelta

from config.settings import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis-based cache manager for application data."""
    
    def __init__(self):
        self.redis_client = None
        self.default_ttl = 300  # 5 minutes
        
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = aioredis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis cache")
            
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis cache")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            if not self.redis_client:
                return None
            
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {str(e)}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            if not self.redis_client:
                return False
            
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            
            await self.redis_client.setex(key, ttl, serialized_value)
            return True
            
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if not self.redis_client:
                return False
            
            result = await self.redis_client.delete(key)
            return bool(result)
            
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if not self.redis_client:
                return False
            
            result = await self.redis_client.exists(key)
            return bool(result)
            
        except Exception as e:
            logger.warning(f"Cache exists check error for key {key}: {str(e)}")
            return False
    
    async def get_keys_pattern(self, pattern: str) -> list:
        """Get all keys matching pattern."""
        try:
            if not self.redis_client:
                return []
            
            keys = await self.redis_client.keys(pattern)
            return keys
            
        except Exception as e:
            logger.warning(f"Cache keys pattern error for {pattern}: {str(e)}")
            return []
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            if not self.redis_client:
                return 0
            
            keys = await self.get_keys_pattern(pattern)
            if keys:
                result = await self.redis_client.delete(*keys)
                return result
            return 0
            
        except Exception as e:
            logger.warning(f"Cache clear pattern error for {pattern}: {str(e)}")
            return 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value in cache."""
        try:
            if not self.redis_client:
                return 0
            
            result = await self.redis_client.incrby(key, amount)
            return result
            
        except Exception as e:
            logger.warning(f"Cache increment error for key {key}: {str(e)}")
            return 0
    
    async def set_hash(self, key: str, field_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set hash values in cache."""
        try:
            if not self.redis_client:
                return False
            
            # Convert values to strings
            string_values = {k: json.dumps(v, default=str) for k, v in field_values.items()}
            
            await self.redis_client.hset(key, mapping=string_values)
            
            if ttl:
                await self.redis_client.expire(key, ttl)
            
            return True
            
        except Exception as e:
            logger.warning(f"Cache set hash error for key {key}: {str(e)}")
            return False
    
    async def get_hash(self, key: str, field: Optional[str] = None) -> Optional[Any]:
        """Get hash value(s) from cache."""
        try:
            if not self.redis_client:
                return None
            
            if field:
                value = await self.redis_client.hget(key, field)
                if value:
                    return json.loads(value)
                return None
            else:
                values = await self.redis_client.hgetall(key)
                if values:
                    return {k: json.loads(v) for k, v in values.items()}
                return None
                
        except Exception as e:
            logger.warning(f"Cache get hash error for key {key}: {str(e)}")
            return None


# Global cache manager instance
cache_manager = CacheManager()


async def get_cache(key: str) -> Optional[Any]:
    """Convenience function to get from cache."""
    return await cache_manager.get(key)


async def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Convenience function to set cache."""
    return await cache_manager.set(key, value, ttl)


async def delete_cache(key: str) -> bool:
    """Convenience function to delete from cache."""
    return await cache_manager.delete(key)


async def clear_cache_pattern(pattern: str) -> int:
    """Convenience function to clear cache pattern."""
    return await cache_manager.clear_pattern(pattern)


class CacheDecorator:
    """Decorator for caching function results."""
    
    def __init__(self, key_prefix: str, ttl: int = 300):
        self.key_prefix = key_prefix
        self.ttl = ttl
    
    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{self.key_prefix}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache first
            cached_result = await get_cache(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            await set_cache(cache_key, result, self.ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        
        return wrapper


class CacheMetrics:
    """Cache performance metrics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0
        self.start_time = datetime.utcnow()
    
    def record_hit(self):
        """Record cache hit."""
        self.hits += 1
    
    def record_miss(self):
        """Record cache miss."""
        self.misses += 1
    
    def record_error(self):
        """Record cache error."""
        self.errors += 1
    
    def get_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        uptime = datetime.utcnow() - self.start_time
        
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "hit_rate": self.get_hit_rate(),
            "total_requests": self.hits + self.misses,
            "uptime_seconds": uptime.total_seconds()
        }
    
    def reset(self):
        """Reset metrics."""
        self.hits = 0
        self.misses = 0
        self.errors = 0
        self.start_time = datetime.utcnow()


# Global metrics instance
cache_metrics = CacheMetrics()


async def get_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics."""
    try:
        # Basic metrics
        stats = cache_metrics.get_stats()
        
        # Redis info if available
        if cache_manager.redis_client:
            try:
                redis_info = await cache_manager.redis_client.info()
                stats["redis_info"] = {
                    "used_memory": redis_info.get("used_memory_human"),
                    "connected_clients": redis_info.get("connected_clients"),
                    "total_commands_processed": redis_info.get("total_commands_processed"),
                    "keyspace_hits": redis_info.get("keyspace_hits"),
                    "keyspace_misses": redis_info.get("keyspace_misses")
                }
            except Exception as e:
                logger.warning(f"Failed to get Redis info: {str(e)}")
        
        return stats
        
    except Exception as e:
        logger.error(f"Cache stats error: {str(e)}")
        return {"error": str(e)}


async def warm_cache():
    """Warm up cache with frequently accessed data."""
    try:
        logger.info("Starting cache warm-up")
        
        # Pre-load common region data
        common_regions = [
            {"lat": 12.9716, "lon": 77.5946, "name": "Bengaluru"},
            {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai"},
            {"lat": 28.7041, "lon": 77.1025, "name": "Delhi"},
            {"lat": 13.0827, "lon": 80.2707, "name": "Chennai"},
            {"lat": 22.5726, "lon": 88.3639, "name": "Kolkata"}
        ]
        
        for region in common_regions:
            cache_key = f"region_info:{region['lat']}:{region['lon']}"
            await set_cache(cache_key, region, ttl=3600)  # Cache for 1 hour
        
        logger.info("Cache warm-up completed")
        
    except Exception as e:
        logger.error(f"Cache warm-up error: {str(e)}")


async def cleanup_expired_cache():
    """Clean up expired cache entries."""
    try:
        # This is handled automatically by Redis TTL
        # But we can implement custom cleanup logic here
        logger.info("Cache cleanup completed")
        
    except Exception as e:
        logger.error(f"Cache cleanup error: {str(e)}")
