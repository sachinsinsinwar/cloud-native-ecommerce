"""
Authentication Routes Module

This module handles user authentication endpoints:
- POST /api/auth/signup - User registration
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
- GET /api/auth/me - Get current user information
"""

from flask import Blueprint, request, jsonify
from models import db, User, Cart
from utils.auth_middleware import generate_token, token_required

# Create Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Register a new user
    
    Expected JSON body:
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    
    Returns:
        201: User created successfully with JWT token
        400: Missing required fields or validation error
        409: Username or email already exists
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Missing required fields: username, email, password'}), 400
    
    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    
    # Validate field lengths
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Create a cart for the new user
        cart = Cart(user_id=new_user.id)
        db.session.add(cart)
        db.session.commit()
        
        # Generate JWT token
        token = generate_token(new_user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token
    
    Expected JSON body:
    {
        "username": "string",  // or "email"
        "password": "string"
    }
    
    Returns:
        200: Login successful with JWT token
        400: Missing required fields
        401: Invalid credentials
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or 'password' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    password = data['password']
    
    # User can login with either username or email
    user = None
    if 'username' in data:
        user = User.query.filter_by(username=data['username'].strip()).first()
    elif 'email' in data:
        user = User.query.filter_by(email=data['email'].strip().lower()).first()
    else:
        return jsonify({'error': 'Provide either username or email'}), 400
    
    # Verify user exists and password is correct
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = generate_token(user.id)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """
    Logout user (client-side token deletion)
    
    Note: With JWT, logout is primarily handled client-side by removing the token.
    This endpoint exists for consistency and can be extended for token blacklisting.
    
    Returns:
        200: Logout successful
    """
    # In a more advanced implementation, you could:
    # 1. Add token to a Redis blacklist
    # 2. Clear any server-side session data
    # 3. Log the logout event
    
    return jsonify({
        'message': 'Logout successful',
        'instructions': 'Please remove the JWT token from client storage'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """
    Get current authenticated user's information
    
    Requires: Authorization header with valid JWT token
    
    Returns:
        200: User information
        401: Invalid or missing token
    """
    return jsonify({
        'user': current_user.to_dict()
    }), 200


@auth_bp.route('/check', methods=['GET'])
@token_required
def check_auth(current_user):
    """
    Check if the provided token is valid
    
    Useful for frontend to verify authentication status
    
    Returns:
        200: Token is valid
        401: Invalid or expired token
    """
    return jsonify({
        'authenticated': True,
        'user_id': current_user.id,
        'username': current_user.username
    }), 200
