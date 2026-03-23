"""
Application Configuration Module

This module manages configuration for different environments (development, testing, production).
It handles database connections, Redis configuration, and security settings.
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class with common settings"""
    
    # Secret key for JWT token signing and session management
    # In production, this MUST be set via environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # JWT token expiration time
    JWT_EXPIRATION_DELTA = timedelta(hours=24)
    
    # Database configuration
    # Format for PostgreSQL: postgresql://username:password@host:port/database
    # Format for SQLite: sqlite:///database_name.db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///ecommerce.db'  # Default to SQLite for easier local development
    
    # Disable SQLAlchemy modification tracking (saves resources)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration for caching and session management
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Cache configuration
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes for general caching
    POPULAR_PRODUCTS_CACHE_TIMEOUT = 600  # 10 minutes for popular products
    
    # Pagination settings
    PRODUCTS_PER_PAGE = 20
    
    # CORS settings - in production, restrict to specific origins
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = False
    TESTING = True
    # Use separate test database
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/ecommerce_test_db'


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    # In production, DATABASE_URL and REDIS_URL MUST be set via environment variables
    # SECRET_KEY must also be a strong random value


# Configuration dictionary for easy access
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
