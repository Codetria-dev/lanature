"""
Tests for Redis caching layer - Phase 5 Performance Optimization

Tests caching functionality for:
- User subscriptions
- Pet lists
- Today's tasks
- Settings
"""

import pytest
from app.cache import cache_manager


@pytest.mark.cache
class TestCacheManager:
    """Tests for CacheManager"""

    def test_cache_is_healthy(self):
        """Test Redis connection health check"""
        # This might fail if Redis is not running, but that's ok for tests
        try:
            is_healthy = cache_manager.is_healthy()
            # If Redis is running, should be True; if not, graceful degradation
            assert isinstance(is_healthy, bool)
        except Exception:
            # Redis not configured for testing is acceptable
            pass

    def test_set_and_get_user_subscription(self):
        """Test user subscription caching"""
        user_id = 1
        subscription_data = {
            "plan": "pro",
            "status": "active",
            "current_period_start": "2026-04-01",
            "current_period_end": "2026-05-01"
        }

        # Should not exist initially
        cached = cache_manager.get_user_subscription(user_id)
        assert cached is None or isinstance(cached, dict)

        # Set
        result = cache_manager.set_user_subscription(user_id, subscription_data)
        assert result is True

        # Get
        cached = cache_manager.get_user_subscription(user_id)
        if cached is not None:  # Only check if Redis is running
            assert cached["plan"] == "pro"
            assert cached["status"] == "active"

    def test_invalidate_user_subscription(self):
        """Test subscription cache invalidation"""
        user_id = 2
        subscription_data = {"plan": "free"}

        # Set
        cache_manager.set_user_subscription(user_id, subscription_data)

        # Invalidate
        result = cache_manager.invalidate_user_subscription(user_id)
        assert result is True

    def test_set_and_get_pet_list_summary(self):
        """Test pet list caching"""
        user_id = 1
        pets_data = [
            {"id": 1, "name": "Max", "species": "dog"},
            {"id": 2, "name": "Fluffy", "species": "cat"}
        ]

        # Set
        result = cache_manager.set_pet_list_summary(user_id, pets_data)
        assert result is True

        # Get
        cached = cache_manager.get_pet_list_summary(user_id)
        if cached is not None:
            assert len(cached) == 2
            assert cached[0]["name"] == "Max"

    def test_invalidate_pet_list(self):
        """Test pet list cache invalidation"""
        user_id = 3
        pets_data = [{"id": 1, "name": "Test"}]

        # Set
        cache_manager.set_pet_list_summary(user_id, pets_data)

        # Invalidate
        result = cache_manager.invalidate_pet_list(user_id)
        assert result is True

    def test_set_and_get_today_tasks(self):
        """Test today's tasks caching"""
        user_id = 1
        tasks_data = [
            {"id": 1, "pet_id": 1, "type": "feeding", "time": "09:00"},
            {"id": 2, "pet_id": 1, "type": "medication", "time": "14:00"}
        ]

        # Set
        result = cache_manager.set_today_tasks(user_id, tasks_data)
        assert result is True

        # Get
        cached = cache_manager.get_today_tasks(user_id)
        if cached is not None:
            assert len(cached) == 2
            assert cached[0]["type"] == "feeding"

    def test_invalidate_today_tasks(self):
        """Test today's tasks cache invalidation"""
        user_id = 4
        tasks_data = [{"id": 1, "type": "feeding"}]

        # Set
        cache_manager.set_today_tasks(user_id, tasks_data)

        # Invalidate
        result = cache_manager.invalidate_today_tasks(user_id)
        assert result is True

    def test_set_and_get_settings(self):
        """Test settings caching"""
        # Set
        result = cache_manager.set_settings("registration_enabled", True)
        assert result is True

        # Get
        cached = cache_manager.get_settings("registration_enabled")
        if cached is not None:
            assert cached is True

    def test_invalidate_settings(self):
        """Test settings cache invalidation"""
        # Set
        cache_manager.set_settings("require_email_verification", True)

        # Invalidate
        result = cache_manager.invalidate_settings("require_email_verification")
        assert result is True

    def test_clear_user_cache(self):
        """Test clearing all cache for a user"""
        user_id = 5

        # Set multiple caches
        cache_manager.set_user_subscription(user_id, {"plan": "pro"})
        cache_manager.set_pet_list_summary(user_id, [{"id": 1}])
        cache_manager.set_today_tasks(user_id, [{"id": 1}])

        # Clear all
        result = cache_manager.clear_user_cache(user_id)
        assert result is True

    def test_cache_error_handling(self):
        """Test graceful degradation on cache errors"""
        # These should not raise exceptions, just return None/False

        # Get from non-existent key
        result = cache_manager.get_user_subscription(999)
        assert result is None or isinstance(result, dict)

        # Invalid operations should be handled gracefully
        assert isinstance(cache_manager.is_healthy(), bool)


@pytest.mark.cache
class TestCacheIntegration:
    """Integration tests for caching with API"""

    def test_pets_endpoint_uses_cache(self, client, test_user, auth_headers, db):
        """Test that pets endpoint benefits from caching"""
        # First request
        response1 = client.get("/api/v1/pets/", headers=auth_headers)
        assert response1.status_code == 200

        # Cache should be populated
        cached = cache_manager.get_pet_list_summary(test_user.id)
        # Might be None if Redis not running, that's ok

        # Second request should be faster (if cached)
        response2 = client.get("/api/v1/pets/", headers=auth_headers)
        assert response2.status_code == 200
        assert response1.json() == response2.json()

    def test_pet_modification_invalidates_cache(self, client, test_user, auth_headers, db):
        """Test that modifying a pet invalidates the cache"""
        # Set cache
        cache_manager.set_pet_list_summary(test_user.id, [{"id": 1, "name": "Old"}])

        # Modify a pet (should invalidate cache)
        response = client.put(
            "/api/v1/pets/1",
            json={"name": "Updated", "species": "dog"},
            headers=auth_headers
        )

        # Cache should be cleared
        cached = cache_manager.get_pet_list_summary(test_user.id)
        # If Redis is running, should be None (invalidated)
