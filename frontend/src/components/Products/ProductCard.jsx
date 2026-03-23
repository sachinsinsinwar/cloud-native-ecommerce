/**
 * Product Card Component
 * 
 * Displays individual product information in a card format.
 * Includes product image, name, price, and Add to Cart button.
 */

import React, { useState } from 'react';
import { cartAPI } from '../../services/api';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const ProductCard = ({ product, onAddToCart }) => {
    const { isAuthenticated } = useAuth();
    const navigate = useNavigate();
    const [adding, setAdding] = useState(false);
    const [message, setMessage] = useState('');

    /**
     * Handle adding product to cart
     */
    const handleAddToCart = async () => {
        // Redirect to login if not authenticated
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }

        setAdding(true);
        setMessage('');

        try {
            await cartAPI.addToCart({
                product_id: product.id,
                quantity: 1,
            });

            // Show success message
            setMessage('Added to cart!');

            // Call parent callback if provided
            if (onAddToCart) {
                onAddToCart();
            }

            // Clear message after 2 seconds
            setTimeout(() => setMessage(''), 2000);
        } catch (err) {
            const errorMsg = err.response?.data?.error || 'Failed to add to cart';
            setMessage(errorMsg);
            setTimeout(() => setMessage(''), 3000);
        } finally {
            setAdding(false);
        }
    };

    return (
        <div className="product-card">
            {/* Product image */}
            <div className="product-image">
                <img
                    src={product.image_url || 'https://via.placeholder.com/300x300?text=No+Image'}
                    alt={product.name}
                    onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/300x300?text=No+Image';
                    }}
                />

                {/* Stock badge */}
                {product.stock === 0 && (
                    <div className="stock-badge out-of-stock">Out of Stock</div>
                )}
                {product.stock > 0 && product.stock < 10 && (
                    <div className="stock-badge low-stock">Only {product.stock} left</div>
                )}
            </div>

            {/* Product details */}
            <div className="product-info">
                {/* Category */}
                {product.category && (
                    <div className="product-category">{product.category}</div>
                )}

                {/* Product name */}
                <h3 className="product-name">{product.name}</h3>

                {/* Product description (truncated) */}
                {product.description && (
                    <p className="product-description">
                        {product.description.length > 100
                            ? `${product.description.substring(0, 100)}...`
                            : product.description}
                    </p>
                )}

                {/* Price and actions */}
                <div className="product-footer">
                    <div className="product-price">${product.price.toFixed(2)}</div>

                    <button
                        className={`btn btn-add-cart ${adding ? 'loading' : ''}`}
                        onClick={handleAddToCart}
                        disabled={adding || product.stock === 0}
                    >
                        {adding ? 'Adding...' : product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
                    </button>
                </div>

                {/* Success/Error message */}
                {message && (
                    <div className={`cart-message ${message.includes('Failed') ? 'error' : 'success'}`}>
                        {message}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProductCard;
