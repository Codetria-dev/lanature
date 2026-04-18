/**
 * useCache hook - Phase 5 Performance Optimization
 *
 * Provides client-side caching for API responses using sessionStorage
 *
 * Usage:
 *   const { data, loading, error } = useCache(
 *     'pets',  // cache key
 *     () => api.get('/pets'),  // fetch function
 *     5 * 60 * 1000  // TTL in ms (default: 5 minutes)
 *   );
 */

import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for caching API responses
 *
 * @param {string} key - Cache key (unique identifier)
 * @param {Function} fetchFn - Async function that fetches data
 * @param {number} ttl - Time-to-live in milliseconds (default: 5 minutes)
 * @returns {Object} { data, loading, error, refresh, clear }
 */
export function useCache(key, fetchFn, ttl = 5 * 60 * 1000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastFetch, setLastFetch] = useState(null);

  // Get cache key with TTL
  const cacheKey = `cache:${key}`;
  const expiryKey = `cache:${key}:expiry`;

  // Check if cache is still valid
  const isCacheValid = useCallback(() => {
    const expiry = sessionStorage.getItem(expiryKey);
    if (!expiry) return false;
    return new Date().getTime() < parseInt(expiry);
  }, [expiryKey]);

  // Load data from cache or fetch
  const load = useCallback(async () => {
    try {
      // Check if cache is valid
      if (isCacheValid()) {
        const cached = sessionStorage.getItem(cacheKey);
        if (cached) {
          setData(JSON.parse(cached));
          setLoading(false);
          setError(null);
          return;
        }
      }

      // Fetch new data
      setLoading(true);
      setError(null);

      const result = await fetchFn();
      const responseData = result.data || result;

      // Store in cache
      sessionStorage.setItem(cacheKey, JSON.stringify(responseData));
      sessionStorage.setItem(expiryKey, (new Date().getTime() + ttl).toString());

      setData(responseData);
      setLastFetch(new Date());
      setLoading(false);
    } catch (err) {
      setError(err);
      setLoading(false);

      // Try to return cached data even if stale
      const cached = sessionStorage.getItem(cacheKey);
      if (cached) {
        setData(JSON.parse(cached));
      }
    }
  }, [fetchFn, cacheKey, expiryKey, ttl, isCacheValid]);

  // Load on mount and when fetchFn/key changes
  useEffect(() => {
    load();
  }, [load]);

  // Refresh data (bypass cache)
  const refresh = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const result = await fetchFn();
      const responseData = result.data || result;

      // Update cache
      sessionStorage.setItem(cacheKey, JSON.stringify(responseData));
      sessionStorage.setItem(expiryKey, (new Date().getTime() + ttl).toString());

      setData(responseData);
      setLastFetch(new Date());
      setLoading(false);
    } catch (err) {
      setError(err);
      setLoading(false);
    }
  }, [fetchFn, cacheKey, expiryKey, ttl]);

  // Clear cache
  const clear = useCallback(() => {
    sessionStorage.removeItem(cacheKey);
    sessionStorage.removeItem(expiryKey);
    setData(null);
    setError(null);
  }, [cacheKey, expiryKey]);

  return {
    data,
    loading,
    error,
    refresh,
    clear,
    lastFetch,
  };
}

/**
 * useLocalCache hook - Persistent cache across sessions
 *
 * Usage:
 *   const { data, loading } = useLocalCache(
 *     'user-settings',
 *     () => api.get('/auth/me'),
 *     24 * 60 * 60 * 1000  // 24 hours
 *   );
 */
export function useLocalCache(key, fetchFn, ttl = 24 * 60 * 60 * 1000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const cacheKey = `locache:${key}`;
  const expiryKey = `locache:${key}:expiry`;

  const isCacheValid = useCallback(() => {
    const expiry = localStorage.getItem(expiryKey);
    if (!expiry) return false;
    return new Date().getTime() < parseInt(expiry);
  }, [expiryKey]);

  const load = useCallback(async () => {
    try {
      // Check cache
      if (isCacheValid()) {
        const cached = localStorage.getItem(cacheKey);
        if (cached) {
          setData(JSON.parse(cached));
          return;
        }
      }

      // Fetch
      setLoading(true);
      const result = await fetchFn();
      const responseData = result.data || result;

      // Store
      localStorage.setItem(cacheKey, JSON.stringify(responseData));
      localStorage.setItem(expiryKey, (new Date().getTime() + ttl).toString());

      setData(responseData);
      setLoading(false);
    } catch (err) {
      setError(err);
      setLoading(false);
    }
  }, [fetchFn, cacheKey, expiryKey, ttl, isCacheValid]);

  useEffect(() => {
    load();
  }, [load]);

  const clear = useCallback(() => {
    localStorage.removeItem(cacheKey);
    localStorage.removeItem(expiryKey);
    setData(null);
  }, [cacheKey, expiryKey]);

  return { data, loading, error, clear };
}
