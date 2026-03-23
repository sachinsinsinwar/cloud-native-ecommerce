"""
Product Routes Module

This module handles product-related endpoints:
- GET /api/products - List all products with pagination and caching
- GET /api/products/<id> - Get specific product details
- POST /api/products - Create new product (admin only - simplified for demo)
"""

from flask import Blueprint, request, jsonify, current_app
from models import db, Product
from utils.auth_middleware import optional_token
from utils.cache import (
    get_cached_product,
    cache_product,
    get_cached_products_list,
    cache_products_list,
    invalidate_all_products_cache
)

# Create Blueprint for product routes
products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
@optional_token
def get_products(current_user):
    """
    Get list of all products with pagination
    
    Query parameters:
    - page (int): Page number (default: 1)
    - per_page (int): Items per page (default: from config)
    - category (str): Filter by category (optional)
    - search (str): Search in product name/description (optional)
    
    Returns:
        200: List of products with pagination metadata
        
    Note: This endpoint uses Redis caching for improved performance.
    Cache is invalidated when products are created/updated.
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config['PRODUCTS_PER_PAGE'], type=int)
    category = request.args.get('category', None, type=str)
    search = request.args.get('search', None, type=str)
    
    # Limit per_page to prevent abuse
    per_page = min(per_page, 100)
    
    # Build cache key based on query parameters
    cache_key_parts = [f'page:{page}']
    if category:
        cache_key_parts.append(f'cat:{category}')
    if search:
        cache_key_parts.append(f'search:{search}')
    cache_key = 'products:' + ':'.join(cache_key_parts)
    
    # Try to get from cache (only if no filters applied for simplicity)
    if not category and not search:
        cached_data = get_cached_products_list(page)
        if cached_data:
            current_app.logger.info(f'Cache hit for products page {page}')
            return jsonify(cached_data), 200
    
    # Build query
    query = Product.query
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        search_pattern = f'%{search}%'
        query = query.filter(
            db.or_(
                Product.name.ilike(search_pattern),
                Product.description.ilike(search_pattern)
            )
        )
    
    # Execute paginated query
    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Convert products to dictionaries
    products_data = [product.to_dict() for product in pagination.items]
    
    response_data = {
        'products': products_data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }
    
    # Cache the result (only for first page without filters)
    if page == 1 and not category and not search:
        cache_products_list(response_data, page)
        current_app.logger.info(f'Cached products page {page}')
    
    return jsonify(response_data), 200


@products_bp.route('/<int:product_id>', methods=['GET'])
@optional_token
def get_product(current_user, product_id):
    """
    Get detailed information about a specific product
    
    Args:
        product_id (int): Product ID
    
    Returns:
        200: Product details
        404: Product not found
        
    Note: Individual products are cached with a configurable TTL.
    Popular products benefit most from this caching strategy.
    """
    # Try to get from cache first
    cached_product = get_cached_product(product_id)
    if cached_product:
        current_app.logger.info(f'Cache hit for product {product_id}')
        return jsonify({'product': cached_product}), 200
    
    # Get from database
    product = db.session.get(Product, product_id)
    
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    product_data = product.to_dict()
    
    # Cache the product
    cache_product(product_id, product_data)
    current_app.logger.info(f'Cached product {product_id}')
    
    return jsonify({'product': product_data}), 200


@products_bp.route('', methods=['POST'])
def create_product():
    """
    Create a new product
    
    Expected JSON body:
    {
        "name": "string",
        "description": "string",
        "price": number,
        "stock": integer,
        "image_url": "string" (optional),
        "category": "string" (optional)
    }
    
    Returns:
        201: Product created successfully
        400: Missing required fields or validation error
        
    Note: In a production application, this endpoint should require
    admin authentication. For demo purposes, it's left open.
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'price', 'stock']
    if not data or not all(k in data for k in required_fields):
        return jsonify({'error': f'Missing required fields: {", ".join(required_fields)}'}), 400
    
    # Validate data types and values
    try:
        name = data['name'].strip()
        description = data.get('description', '').strip()
        price = float(data['price'])
        stock = int(data['stock'])
        image_url = data.get('image_url', None)
        category = data.get('category', 'General')
        
        if price < 0:
            return jsonify({'error': 'Price cannot be negative'}), 400
        
        if stock < 0:
            return jsonify({'error': 'Stock cannot be negative'}), 400
        
        if len(name) < 3:
            return jsonify({'error': 'Product name must be at least 3 characters'}), 400
        
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid data format: {str(e)}'}), 400
    
    # Create new product
    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=image_url,
        category=category
    )
    
    try:
        db.session.add(new_product)
        db.session.commit()
        
        # Invalidate product list cache since we added a new product
        invalidate_all_products_cache()
        current_app.logger.info('Invalidated product cache after creating new product')
        
        return jsonify({
            'message': 'Product created successfully',
            'product': new_product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create product: {str(e)}'}), 500


@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Get list of all available product categories
    
    Returns:
        200: List of unique categories
    """
    # Query distinct categories from database
    categories = db.session.query(Product.category).distinct().all()
    category_list = [cat[0] for cat in categories if cat[0]]
    
    return jsonify({
        'categories': category_list,
        'count': len(category_list)
    }), 200
