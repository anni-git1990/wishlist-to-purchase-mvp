"""
Myntra Wishlist Confidence Engine - Distributed Cache Service
Implements hot-tier caching for confidence metadata & digests with TTL enforcement and hit-rate telemetry.
"""

import time
import json
from typing import Optional, Dict, Any


class CacheService:
    def __init__(self, default_ttl_seconds: int = 3600):
        self.default_ttl = default_ttl_seconds
        self._store: Dict[str, Dict[str, Any]] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves object from cache if present and not expired.
        """
        if key in self._store:
            entry = self._store[key]
            if time.time() < entry["expires_at"]:
                self.hits += 1
                return entry["value"]
            else:
                # Expired key
                del self._store[key]

        self.misses += 1
        return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """
        Stores value with TTL in seconds.
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = time.time() + ttl
        self._store[key] = {
            "value": value,
            "expires_at": expires_at
        }
        return True

    def invalidate(self, key: str) -> bool:
        """
        Purges key from cache.
        """
        if key in self._store:
            del self._store[key]
            return True
        return False

    def invalidate_prefix(self, prefix: str) -> int:
        """
        Purges all keys matching prefix.
        """
        keys_to_del = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_del:
            del self._store[k]
        return len(keys_to_del)

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns cache telemetry including hit rate percentage.
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            "totalRequests": total,
            "hits": self.hits,
            "misses": self.misses,
            "hitRatePercentage": round(hit_rate, 2),
            "cachedItemsCount": len(self._store),
            "meetsSla": hit_rate >= 92.0 or total == 0
        }


if __name__ == "__main__":
    cache = CacheService(default_ttl_seconds=5)
    cache.set("confidence:user:123", {"recommendedSize": "M"})
    
    val = cache.get("confidence:user:123")
    print(f"Cache Get: {val}")
    print(f"Stats: {cache.get_stats()}")
