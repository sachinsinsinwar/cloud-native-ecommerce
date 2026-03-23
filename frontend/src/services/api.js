/**
 * Axios API Service Configuration
 * 
 * This module configures Axios for making HTTP requests to the backend API.
 * It includes:
 * - Base URL configuration
 * - Request interceptors for adding JWT tokens
 * - Response interceptors for error handling
 */

import axios from 'axios';

// Create Axios instance with base configuration
const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * Request Interceptor
 * Automatically adds JWT token to Authorization header for protected routes
 */
api.interceptors.request.use(
    (config) => {
        // Get token from localStorage
        const token = localStorage.getItem('token');

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

/**
 * Response Interceptor
 * Handles common error scenarios like 401 (unauthorized)
 */
api.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        // Handle 401 Unauthorized - token expired or invalid
        if (error.response && error.response.status === 401) {
            // Clear invalid token
            localStorage.removeItem('token');
            localStorage.removeItem('user');

            // Redirect to login (only if not already on login/signup page)
            if (!window.location.pathname.includes('/login') &&
                !window.location.pathname.includes('/signup')) {
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

// Auth API calls
export const authAPI = {
    /**
     * Register a new user
     * @param {Object} userData - { username, email, password }
     */
    signup: (userData) => api.post('/api/auth/signup', userData),

    /**
     * Login user
     * @param {Object} credentials - { username or email, password }
     */
    login: (credentials) => api.post('/api/auth/login', credentials),

    /**
     * Logout user
     */
    logout: () => api.post('/api/auth/logout'),

    /**
     * Get current user info
     */
    getCurrentUser: () => api.get('/api/auth/me'),

    /**
     * Check if token is valid
     */
    checkAuth: () => api.get('/api/auth/check'),
};

// Products API calls
export const productsAPI = {
    /**
     * Get all products with optional filters
     * @param {Object} params - { page, per_page, category, search }
     */
    getProducts: (params = {}) => api.get('/api/products', { params }),

    /**
     * Get single product by ID
     * @param {number} productId
     */
    getProduct: (productId) => api.get(`/api/products/${productId}`),

    /**
     * Create new product
     * @param {Object} productData
     */
    createProduct: (productData) => api.post('/api/products', productData),

    /**
     * Get available categories
     */
    getCategories: () => api.get('/api/products/categories'),
};

// Cart API calls
export const cartAPI = {
    /**
     * Get current user's cart
     */
    getCart: () => api.get('/api/cart'),

    /**
     * Add item to cart
     * @param {Object} item - { product_id, quantity }
     */
    addToCart: (item) => api.post('/api/cart/items', item),

    /**
     * Update cart item quantity
     * @param {number} itemId
     * @param {number} quantity
     */
    updateCartItem: (itemId, quantity) => api.put(`/api/cart/items/${itemId}`, { quantity }),

    /**
     * Remove item from cart
     * @param {number} itemId
     */
    removeFromCart: (itemId) => api.delete(`/api/cart/items/${itemId}`),

    /**
     * Checkout - create order from cart
     */
    checkout: () => api.post('/api/cart/checkout'),

    /**
     * Clear entire cart
     */
    clearCart: () => api.post('/api/cart/clear'),
};

export default api;
