/**
 * Shopping Cart Component
 * 
 * Displays user's shopping cart with:
 * - List of cart items
 * - Quantity update functionality
 * - Remove item functionality
 * - Total price calculation
 * - Checkout functionality
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { cartAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import './Cart.css';

const ShoppingCart = () => {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();

    // Cart state
    const [cart, setCart] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [processing, setProcessing] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');

    /**
     * Fetch cart data
     */
    const fetchCart = async () => {
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await cartAPI.getCart();
            setCart(response.data.cart);
        } catch (err) {
            setError('Failed to load cart. Please try again.');
            console.error('Error fetching cart:', err);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Update item quantity
     */
    const updateQuantity = async (itemId, newQuantity) => {
        if (newQuantity < 1) return;

        try {
            const response = await cartAPI.updateCartItem(itemId, newQuantity);
            setCart(response.data.cart);
            showSuccessMessage('Quantity updated');
        } catch (err) {
            const errorMsg = err.response?.data?.error || 'Failed to update quantity';
            setError(errorMsg);
            setTimeout(() => setError(''), 3000);
        }
    };

    /**
     * Remove item from cart
     */
    const removeItem = async (itemId) => {
        if (!window.confirm('Remove this item from cart?')) {
            return;
        }

        try {
            const response = await cartAPI.removeFromCart(itemId);
            setCart(response.data.cart);
            showSuccessMessage('Item removed');
        } catch (err) {
            const errorMsg = err.response?.data?.error || 'Failed to remove item';
            setError(errorMsg);
            setTimeout(() => setError(''), 3000);
        }
    };

    /**
     * Clear entire cart
     */
    const clearCart = async () => {
        if (!window.confirm('Clear all items from cart?')) {
            return;
        }

        try {
            const response = await cartAPI.clearCart();
            setCart(response.data.cart);
            showSuccessMessage('Cart cleared');
        } catch (err) {
            setError('Failed to clear cart');
            setTimeout(() => setError(''), 3000);
        }
    };

    /**
     * Checkout - create order
     */
    const handleCheckout = async () => {
        if (!cart || cart.items.length === 0) {
            return;
        }

        if (!window.confirm('Proceed with checkout?')) {
            return;
        }

        setProcessing(true);
        setError('');

        try {
            const response = await cartAPI.checkout();
            const order = response.data.order;

            // Show success message
            alert(`Order placed successfully! Order ID: ${order.id}\nTotal: $${order.total_amount}`);

            // Reload cart (should be empty now)
            await fetchCart();
        } catch (err) {
            const errorMsg = err.response?.data?.error || 'Checkout failed. Please try again.';
            setError(errorMsg);

            // If stock issues, reload cart to show updated availability
            if (err.response?.status === 422) {
                fetchCart();
            }
        } finally {
            setProcessing(false);
        }
    };

    /**
     * Show success message temporarily
     */
    const showSuccessMessage = (message) => {
        setSuccessMessage(message);
        setTimeout(() => setSuccessMessage(''), 2000);
    };

    /**
     * Load cart on mount
     */
    useEffect(() => {
        fetchCart();
    }, []);

    // Loading state
    if (loading) {
        return (
            <div className="cart-container">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading cart...</p>
                </div>
            </div>
        );
    }

    // Empty cart
    if (!cart || cart.items.length === 0) {
        return (
            <div className="cart-container">
                <div className="cart-header">
                    <h1>Shopping Cart</h1>
                </div>
                <div className="empty-cart">
                    <div className="empty-cart-icon">🛒</div>
                    <h2>Your cart is empty</h2>
                    <p>Add some products to get started!</p>
                    <button
                        className="btn btn-primary"
                        onClick={() => navigate('/products')}
                    >
                        Browse Products
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="cart-container">
            {/* Header */}
            <div className="cart-header">
                <h1>Shopping Cart</h1>
                <p className="cart-subtitle">
                    {cart.items.length} {cart.items.length === 1 ? 'item' : 'items'} in your cart
                </p>
            </div>

            {/* Error message */}
            {error && (
                <div className="error-banner">
                    {error}
                </div>
            )}

            {/* Success message */}
            {successMessage && (
                <div className="success-banner">
                    {successMessage}
                </div>
            )}

            {/* Cart content */}
            <div className="cart-content">
                {/* Cart items */}
                <div className="cart-items">
                    {cart.items.map((item) => (
                        <div key={item.id} className="cart-item">
                            {/* Product image */}
                            <div className="cart-item-image">
                                <img
                                    src={item.product.image_url || 'https://via.placeholder.com/100'}
                                    alt={item.product.name}
                                    onError={(e) => {
                                        e.target.src = 'https://via.placeholder.com/100';
                                    }}
                                />
                            </div>

                            {/* Product details */}
                            <div className="cart-item-details">
                                <h3>{item.product.name}</h3>
                                <p className="item-category">{item.product.category}</p>
                                <p className="item-price">${item.product.price.toFixed(2)} each</p>
                            </div>

                            {/* Quantity controls */}
                            <div className="cart-item-quantity">
                                <button
                                    className="quantity-btn"
                                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                    disabled={item.quantity <= 1}
                                >
                                    −
                                </button>
                                <span className="quantity-value">{item.quantity}</span>
                                <button
                                    className="quantity-btn"
                                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                    disabled={item.quantity >= item.product.stock}
                                >
                                    +
                                </button>
                            </div>

                            {/* Subtotal */}
                            <div className="cart-item-subtotal">
                                ${item.subtotal.toFixed(2)}
                            </div>

                            {/* Remove button */}
                            <button
                                className="cart-item-remove"
                                onClick={() => removeItem(item.id)}
                                title="Remove item"
                            >
                                ✕
                            </button>
                        </div>
                    ))}

                    {/* Clear cart button */}
                    <div className="cart-actions">
                        <button className="btn btn-secondary" onClick={clearCart}>
                            Clear Cart
                        </button>
                    </div>
                </div>

                {/* Cart summary */}
                <div className="cart-summary">
                    <h2>Order Summary</h2>

                    <div className="summary-row">
                        <span>Subtotal</span>
                        <span>${cart.total.toFixed(2)}</span>
                    </div>

                    <div className="summary-row">
                        <span>Shipping</span>
                        <span>FREE</span>
                    </div>

                    <div className="summary-row total">
                        <span>Total</span>
                        <span>${cart.total.toFixed(2)}</span>
                    </div>

                    <button
                        className="btn btn-primary btn-checkout"
                        onClick={handleCheckout}
                        disabled={processing || cart.items.length === 0}
                    >
                        {processing ? 'Processing...' : 'Proceed to Checkout'}
                    </button>

                    <button
                        className="btn btn-secondary"
                        onClick={() => navigate('/products')}
                    >
                        Continue Shopping
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ShoppingCart;
