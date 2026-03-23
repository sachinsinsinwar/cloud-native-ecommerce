"""
Authentication Middleware Module

This module provides JWT token generation, validation, and authentication decorators.
It handles secure user authentication for protected API endpoints.
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from models import User


def generate_token(user_id):
    """
    Generate a JWT token for authenticated user
    
    Args:
        user_id (int): User's database ID
        
    Returns:
        str: Encoded JWT token containing user_id and expiration
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + current_app.config['JWT_EXPIRATION_DELTA'],
        'iat': datetime.utcnow()  # Issued at time
    }
    
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token


def decode_token(token):
    """
    Decode and validate a JWT token
    
    Args:
        token (str): JWT token to decode
        
    Returns:
        dict: Decoded payload containing user_id, or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid
        return None


def token_required(f):
    """
    Decorator for protecting routes that require authentication
    
    This decorator:
    1. Extracts the JWT token from Authorization header
    2. Validates the token
    3. Retrieves the user from database
    4. Passes the user object to the decorated function
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify({'message': f'Hello {current_user.username}'})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if Authorization header exists
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            
            # Expected format: "Bearer <token>"
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format. Use: Bearer <token>'}), 401
        
        # No token provided
        if not token:
            return jsonify({'error': 'Authentication token is missing'}), 401
        
        # Decode and validate token
        payload = decode_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Get user from database
        from models import db
        current_user = db.session.get(User, payload['user_id'])
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 401
        
        # Pass current_user to the decorated function
        return f(current_user, *args, **kwargs)
    
    return decorated


def optional_token(f):
    """
    Decorator for routes where authentication is optional
    
    Similar to token_required but allows requests without tokens.
    If token is present and valid, current_user is passed; otherwise None is passed.
    
    Usage:
        @app.route('/products')
        @optional_token
        def get_products(current_user):
            # current_user will be None if not authenticated
            if current_user:
                # Show personalized content
                pass
            else:
                # Show public content
                pass
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        current_user = None
        
        # Try to get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
                payload = decode_token(token)
                
                if payload:
                    from models import db
                    current_user = db.session.get(User, payload['user_id'])
            except (IndexError, Exception):
                # Invalid token format or other error - just proceed without user
                pass
        
        # Pass current_user (or None) to the decorated function
        return f(current_user, *args, **kwargs)
    
    return decorated
