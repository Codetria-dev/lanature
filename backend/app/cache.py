"""
Caching layer for LaNature API - Phase 5 Performance Optimization

Manages Redis caching for frequently accessed data:
- User subscription status (24h TTL)
- Pet list with routine summary (1h TTL)
- Active tasks for today (1h TTL)
- User settings (7d TTL)

Usage:
    from app.cache import cache_manager

    # Get cached or fetch
    subscription = cache_manager.get_user_subscription(user_id)

    # Invalidate cache
    cache_manager.invalidate_user_subscription(user_id)

Note: Redis is optional. If not available, caching gracefully degrades.
"""

import json
import os
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

# Try to import redis, but gracefully degrade if not available
try:
    import redis
    REDIS_AVAILABLE = True
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)
        redis_client.ping()  # Test connection
    except Exception as e:
        print(f"[WARNING] Redis not available ({e}), using in-memory cache")
        redis_client = None
        REDIS_AVAILABLE = False
except ImportError:
    REDIS_AVAILABLE = False
    redis_client = None


class CacheManager:
    """
    Manages caching of frequently accessed data using Redis.

    Gracefully degrades when Redis is not available - returns None,
    which signals the application to fetch from database.

    TTL Strategy:
    - User data: 24 hours (subscription changes infrequently)
    - Pet data: 1 hour (more volatile)
    - Task data: 1 hour (daily rotations)
    - Settings: 7 days (rarely change)
    """

    # TTL constants (in seconds)
    TTL_USER_SUBSCRIPTION = 24 * 60 * 60  # 24 hours
    TTL_PET_LIST = 60 * 60  # 1 hour
    TTL_TODAY_TASKS = 60 * 60  # 1 hour
    TTL_SETTINGS = 7 * 24 * 60 * 60  # 7 days

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.enabled = redis_client is not None

    # =====================
    # User Subscription Cache
    # =====================

    def get_user_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached user subscription status.

        Returns None if not in cache or Redis unavailable (caller should fetch from DB).
        """
        if not self.enabled:
            return None

        try:
            key = f"user:{user_id}:subscription"
            cached = self.redis.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            print(f"Cache get error for user subscription: {e}")
            return None

    def set_user_subscription(self, user_id: int, subscription_data: Dict[str, Any]) -> bool:
        """Set user subscription in cache with TTL."""
        if not self.enabled:
            return False

        try:
            key = f"user:{user_id}:subscription"
            self.redis.setex(
                key,
                self.TTL_USER_SUBSCRIPTION,
                json.dumps(subscription_data, default=str)
            )
            return True
        except Exception as e:
            print(f"Cache set error for user subscription: {e}")
            return False

    def invalidate_user_subscription(self, user_id: int) -> bool:
        """Remove user subscription from cache."""
        if not self.enabled:
            return True  # No-op is success

        try:
            key = f"user:{user_id}:subscription"
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return False

    # =====================
    # Pet List Cache
    # =====================

    def get_pet_list_summary(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached pet list with routine summary.

        Returns None if not in cache or Redis unavailable.
        """
        if not self.enabled:
            return None

        try:
            key = f"user:{user_id}:pets:summary"
            cached = self.redis.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            print(f"Cache get error for pet list: {e}")
            return None

    def set_pet_list_summary(self, user_id: int, pets_data: List[Dict[str, Any]]) -> bool:
        """Set pet list in cache with TTL."""
        if not self.enabled:
            return False

        try:
            key = f"user:{user_id}:pets:summary"
            self.redis.setex(
                key,
                self.TTL_PET_LIST,
                json.dumps(pets_data, default=str)
            )
            return True
        except Exception as e:
            print(f"Cache set error for pet list: {e}")
            return False

    def invalidate_pet_list(self, user_id: int) -> bool:
        """Remove pet list from cache (call after pet changes)."""
        if not self.enabled:
            return True

        try:
            key = f"user:{user_id}:pets:summary"
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return False

    # =====================
    # Today's Tasks Cache
    # =====================

    def get_today_tasks(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get cached today's active tasks for user."""
        if not self.enabled:
            return None

        try:
            key = f"user:{user_id}:tasks:today"
            cached = self.redis.get(key)
            return json.loads(cached) if cached else None
        except Exception as e:
            print(f"Cache get error for today tasks: {e}")
            return None

    def set_today_tasks(self, user_id: int, tasks_data: List[Dict[str, Any]]) -> bool:
        """Set today's tasks in cache with TTL."""
        if not self.enabled:
            return False

        try:
            key = f"user:{user_id}:tasks:today"
            self.redis.setex(
                key,
                self.TTL_TODAY_TASKS,
                json.dumps(tasks_data, default=str)
            )
            return True
        except Exception as e:
            print(f"Cache set error for today tasks: {e}")
            return False

    def invalidate_today_tasks(self, user_id: int) -> bool:
        """Remove today's tasks from cache (call after task changes)."""
        if not self.enabled:
            return True

        try:
            key = f"user:{user_id}:tasks:today"
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return False

    # =====================
    # Settings Cache
    # =====================

    def get_settings(self, key: str) -> Optional[Any]:
        """Get cached setting value by key."""
        if not self.enabled:
            return None

        try:
            cache_key = f"settings:{key}"
            cached = self.redis.get(cache_key)
            return json.loads(cached) if cached else None
        except Exception as e:
            print(f"Cache get error for setting {key}: {e}")
            return None

    def set_settings(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set setting in cache with optional custom TTL.

        Args:
            key: Setting key
            value: Setting value (will be JSON-encoded)
            ttl: Optional TTL in seconds (defaults to TTL_SETTINGS)
        """
        if not self.enabled:
            return False

        try:
            cache_key = f"settings:{key}"
            ttl = ttl or self.TTL_SETTINGS
            self.redis.setex(
                cache_key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            print(f"Cache set error for setting {key}: {e}")
            return False

    def invalidate_settings(self, key: str) -> bool:
        """Remove setting from cache."""
        if not self.enabled:
            return True

        try:
            cache_key = f"settings:{key}"
            self.redis.delete(cache_key)
            return True
        except Exception as e:
            print(f"Cache invalidate error: {e}")
            return False

    # =====================
    # Health Check
    # =====================

    def is_healthy(self) -> bool:
        """Check if Redis connection is healthy."""
        if not self.enabled:
            return False  # Redis not available, but not an error for development

        try:
            self.redis.ping()
            return True
        except Exception as e:
            print(f"Redis health check failed: {e}")
            return False

    def clear_user_cache(self, user_id: int) -> bool:
        """Clear all cached data for a user."""
        if not self.enabled:
            return True

        try:
            pattern = f"user:{user_id}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache clear error for user {user_id}: {e}")
            return False


# Global cache manager instance
cache_manager = CacheManager(redis_client)
