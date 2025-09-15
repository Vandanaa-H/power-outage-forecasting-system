import asyncio
import json
from typing import Any, Optional
from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Simple in-memory cache manager for demo purposes."""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
        self.enabled = True
        
    async def initialize(self):
        """Initialize cache (no-op for in-memory cache)."""
        logger.info("Initialized in-memory cache for demo")
        
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.enabled or key not in self._cache:
            return None
            
        # Check expiry
        if key in self._expiry and datetime.utcnow() > self._expiry[key]:
            del self._cache[key]
            del self._expiry[key]
            return None
            
        return self._cache[key]
        
    async def set(self, key: str, value: str, ttl: int = 3600):
        """Set value in cache with TTL."""
        if not self.enabled:
            return
            
        self._cache[key] = value
        self._expiry[key] = datetime.utcnow() + timedelta(seconds=ttl)
        
    async def delete(self, key: str):
        """Delete key from cache."""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self._cache
        
    async def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
        self._expiry.clear()
        
    async def close(self):
        """Close cache connection (no-op for in-memory)."""
        logger.info("Closed in-memory cache")
        
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from cache."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON for key: {key}")
        return None
        
    async def set_json(self, key: str, value: dict, ttl: int = 3600):
        """Set JSON value in cache."""
        await self.set(key, json.dumps(value), ttl)
        
    def cache_key(self, *args) -> str:
        """Generate cache key from arguments."""
        return ":".join(str(arg) for arg in args)
        
    async def get_stats(self) -> dict:
        """Get cache statistics."""
        now = datetime.utcnow()
        expired_keys = [k for k, exp in self._expiry.items() if now > exp]
        
        return {
            "total_keys": len(self._cache),
            "expired_keys": len(expired_keys),
            "memory_usage": "N/A (in-memory)",
            "hit_rate": "N/A",
            "enabled": self.enabled
        }
