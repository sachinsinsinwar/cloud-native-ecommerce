"""
Shopping Cart Routes Module

This module handles shopping cart management endpoints:
- GET /api/cart - Get current user's cart
- POST /api/cart/items - Add item to cart
- PUT /api/cart/items/<id> - Update cart item quantity
- DELETE /api/cart/items/<id> - Remove item from cart
- POST /api/cart/checkout - Create order from cart
"""

from flask import Blueprint, request, jsonify
from models import db, Cart, CartItem, Product, Order, OrderItem
from utils.auth_middleware import token_required

# Create Blueprint for cart routes
cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


@cart_bp.route('', methods=['GET'])
@token_required
def get_cart(current_user):
    """
    Get current user's shopping cart with all items
    
    Requires: Authorization header with valid JWT token
    
    Returns:
        200: Cart with items and total
        404: Cart not found (should not happen if created on signup)
    """
    # Get user's cart (should exist from signup)
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart:
        # Create cart if it doesn't exist (fallback)
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    return jsonify({
        'cart': cart.to_dict()
    }), 200


@cart_bp.route('/items', methods=['POST'])
@token_required
def add_to_cart(current_user):
    """
    Add a product to the shopping cart
    
    Expected JSON body:
    {
        "product_id": integer,
        "quantity": integer (default: 1)
    }
    
    Returns:
        200: Item added successfully (or quantity updated if already in cart)
        400: Missing required fields or invalid data
        404: Product not found
        422: Insufficient stock
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or 'product_id' not in data:
        return jsonify({'error': 'Missing required field: product_id'}), 400
    
    try:
        product_id = int(data['product_id'])
        quantity = int(data.get('quantity', 1))
        
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
            
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid data format'}), 400
    
    # Check if product exists
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    # Check stock availability
    if product.stock < quantity:
        return jsonify({
            'error': 'Insufficient stock',
            'available': product.stock,
            'requested': quantity
        }), 422
    
    # Get user's cart
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.flush()  # Get cart.id without committing
    
    # Check if product already in cart
    cart_item = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id
    ).first()
    
    try:
        if cart_item:
            # Update quantity
            new_quantity = cart_item.quantity + quantity
            
            # Check stock for new quantity
            if product.stock < new_quantity:
                return jsonify({
                    'error': 'Insufficient stock',
                    'available': product.stock,
                    'current_in_cart': cart_item.quantity,
                    'requested_addition': quantity
                }), 422
            
            cart_item.quantity = new_quantity
            message = 'Cart item quantity updated'
        else:
            # Add new item to cart
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(cart_item)
            message = 'Item added to cart'
        
        db.session.commit()
        
        # Return updated cart
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        
        return jsonify({
            'message': message,
            'cart': cart.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update cart: {str(e)}'}), 500


@cart_bp.route('/items/<int:item_id>', methods=['PUT'])
@token_required
def update_cart_item(current_user, item_id):
    """
    Update quantity of a cart item
    
    Args:
        item_id (int): Cart item ID
        
    Expected JSON body:
    {
        "quantity": integer
    }
    
    Returns:
        200: Item quantity updated
        400: Invalid quantity
        403: Item does not belong to user's cart
        404: Cart item not found
        422: Insufficient stock
    """
    data = request.get_json()
    
    if not data or 'quantity' not in data:
        return jsonify({'error': 'Missing required field: quantity'}), 400
    
    try:
        quantity = int(data['quantity'])
        
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive. Use DELETE to remove item.'}), 400
            
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quantity format'}), 400
    
    # Get cart item
    cart_item = db.session.get(CartItem, item_id)
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    # Verify item belongs to user's cart
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart_item.cart_id != cart.id:
        return jsonify({'error': 'Unauthorized access to cart item'}), 403
    
    # Check stock availability
    if cart_item.product.stock < quantity:
        return jsonify({
            'error': 'Insufficient stock',
            'available': cart_item.product.stock,
            'requested': quantity
        }), 422
    
    # Update quantity
    try:
        cart_item.quantity = quantity
        db.session.commit()
        
        # Return updated cart
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        
        return jsonify({
            'message': 'Cart item updated',
            'cart': cart.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update cart item: {str(e)}'}), 500


@cart_bp.route('/items/<int:item_id>', methods=['DELETE'])
@token_required
def remove_from_cart(current_user, item_id):
    """
    Remove an item from the shopping cart
    
    Args:
        item_id (int): Cart item ID
    
    Returns:
        200: Item removed successfully
        403: Item does not belong to user's cart
        404: Cart item not found
    """
    # Get cart item
    cart_item = db.session.get(CartItem, item_id)
    
    if not cart_item:
        return jsonify({'error': 'Cart item not found'}), 404
    
    # Verify item belongs to user's cart
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if cart_item.cart_id != cart.id:
        return jsonify({'error': 'Unauthorized access to cart item'}), 403
    
    # Remove item
    try:
        db.session.delete(cart_item)
        db.session.commit()
        
        # Return updated cart
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        
        return jsonify({
            'message': 'Item removed from cart',
            'cart': cart.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove cart item: {str(e)}'}), 500


@cart_bp.route('/checkout', methods=['POST'])
@token_required
def checkout(current_user):
    """
    Create an order from current cart contents
    
    This endpoint:
    1. Validates cart is not empty
    2. Checks stock availability for all items
    3. Creates an order with order items
    4. Updates product stock
    5. Clears the cart
    
    Returns:
        201: Order created successfully
        400: Cart is empty
        422: Insufficient stock for one or more items
        500: Order creation failed
    """
    # Get user's cart
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if not cart or not cart.items:
        return jsonify({'error': 'Cart is empty'}), 400
    
    # Verify stock availability for all items
    stock_issues = []
    for item in cart.items:
        if item.product.stock < item.quantity:
            stock_issues.append({
                'product': item.product.name,
                'available': item.product.stock,
                'requested': item.quantity
            })
    
    if stock_issues:
        return jsonify({
            'error': 'Insufficient stock for some items',
            'details': stock_issues
        }), 422
    
    # Calculate total
    total_amount = cart.get_total()
    
    # Create order
    try:
        # Start transaction
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # Get order.id
        
        # Create order items and update stock
        for cart_item in cart.items:
            # Create order item (store price at time of purchase)
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            db.session.add(order_item)
            
            # Update product stock
            cart_item.product.stock -= cart_item.quantity
        
        # Clear cart items
        for cart_item in cart.items:
            db.session.delete(cart_item)
        
        # Commit transaction
        db.session.commit()
        
        # Get complete order with items
        order = db.session.get(Order, order.id)
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create order: {str(e)}'}), 500


@cart_bp.route('/clear', methods=['POST'])
@token_required
def clear_cart(current_user):
    """
    Clear all items from the shopping cart
    
    Returns:
        200: Cart cleared successfully
    """
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    
    if cart:
        try:
            # Delete all cart items
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
            
            return jsonify({
                'message': 'Cart cleared successfully',
                'cart': cart.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to clear cart: {str(e)}'}), 500
    
    return jsonify({'message': 'Cart is already empty'}), 200
