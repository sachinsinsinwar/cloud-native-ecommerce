"""
Redis Caching Utilities Module

This module provides caching functionality using Redis.
It includes utilities for caching product data with TTL (Time To Live) configuration.
"""

import redis
import json
from flask import current_app


class RedisCache:
    """
    Redis cache wrapper for storing and retrieving cached data
    
    This class provides methods for:
    - Connecting to Redis
    - Storing data with expiration
    - Retrieving cached data
    - Invalidating cache entries
    """
    
    def __init__(self, app=None):
        """Initialize Redis cache"""
        self.redis_client = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize Redis connection from Flask app config
        
        Args:
            app: Flask application instance
        """
        redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True  # Automatically decode bytes to strings
            )
            # Test connection
            self.redis_client.ping()
            app.logger.info('Redis connection established successfully')
        except redis.ConnectionError as e:
            app.logger.error(f'Redis connection failed: {e}')
            # Set redis_client to None so we can handle fallback
            self.redis_client = None
    
    def get(self, key):
        """
        Retrieve cached data by key
        
        Args:
            key (str): Cache key
            
        Returns:
            dict or None: Cached data or None if not found/expired
        """
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except (redis.RedisError, json.JSONDecodeError) as e:
            current_app.logger.error(f'Cache get error for key {key}: {e}')
        
        return None
    
    def set(self, key, value, timeout=None):
        """
        Store data in cache with optional expiration
        
        Args:
            key (str): Cache key
            value (dict): Data to cache (must be JSON serializable)
            timeout (int): Expiration time in seconds (None = no expiration)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            serialized_value = json.dumps(value)
            if timeout:
                self.redis_client.setex(key, timeout, serialized_value)
            else:
                self.redis_client.set(key, serialized_value)
            return True
        except (redis.RedisError, TypeError) as e:
            current_app.logger.error(f'Cache set error for key {key}: {e}')
            return False
    
    def delete(self, key):
        """
        Delete cached data by key
        
        Args:
            key (str): Cache key to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except redis.RedisError as e:
            current_app.logger.error(f'Cache delete error for key {key}: {e}')
            return False
    
    def delete_pattern(self, pattern):
        """
        Delete all keys matching a pattern
        
        Args:
            pattern (str): Pattern to match (e.g., 'product:*')
            
        Returns:
            int: Number of keys deleted
        """
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            current_app.logger.error(f'Cache delete pattern error for {pattern}: {e}')
            return 0
    
    def flush_all(self):
        """
        Clear all cached data (use with caution!)
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except redis.RedisError as e:
            current_app.logger.error(f'Cache flush error: {e}')
            return False


# Global cache instance (will be initialized in app.py)
cache = RedisCache()


def cache_product(product_id, product_data, timeout=None):
    """
    Cache a single product's data
    
    Args:
        product_id (int): Product ID
        product_data (dict): Product data to cache
        timeout (int): Cache timeout in seconds (default from config)
    """
    if timeout is None:
        timeout = current_app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
    
    cache.set(f'product:{product_id}', product_data, timeout)


def get_cached_product(product_id):
    """
    Retrieve cached product data
    
    Args:
        product_id (int): Product ID
        
    Returns:
        dict or None: Cached product data or None if not found
    """
    return cache.get(f'product:{product_id}')


def invalidate_product_cache(product_id):
    """
    Invalidate cache for a specific product
    
    Args:
        product_id (int): Product ID
    """
    cache.delete(f'product:{product_id}')


def cache_products_list(products_data, page=1, timeout=None):
    """
    Cache products list for a specific page
    
    Args:
        products_data (list): List of product dictionaries
        page (int): Page number
        timeout (int): Cache timeout in seconds
    """
    if timeout is None:
        timeout = current_app.config.get('POPULAR_PRODUCTS_CACHE_TIMEOUT', 600)
    
    cache.set(f'products:page:{page}', products_data, timeout)


def get_cached_products_list(page=1):
    """
    Retrieve cached products list
    
    Args:
        page (int): Page number
        
    Returns:
        list or None: Cached products list or None if not found
    """
    return cache.get(f'products:page:{page}')


def invalidate_all_products_cache():
    """
    Invalidate all product-related cache entries
    This should be called when products are updated/added/deleted
    """
    cache.delete_pattern('product:*')
    cache.delete_pattern('products:*')


def test_redis_connection():
    """
    Test Redis connection - useful for health checks
    
    Returns:
        bool: True if Redis is connected and responding
    """
    if not cache.redis_client:
        print('❌ Redis is not connected')
        return False
    
    try:
        cache.redis_client.ping()
        print('✅ Redis connection successful')
        return True
    except redis.RedisError as e:
        print(f'❌ Redis connection failed: {e}')
        return False
