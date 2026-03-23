/**
 * Main App Component
 * 
 * Root component that sets up:
 * - React Router for navigation
 * - Authentication context provider
 * - Protected routes
 * - Navigation bar with cart indicator
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Auth/Login';
import Signup from './components/Auth/Signup';
import ProductList from './components/Products/ProductList';
import ShoppingCart from './components/Cart/ShoppingCart';
import './App.css';

/**
 * Navigation Bar Component
 * Displays navigation links and user status
 */
const Navbar = () => {
    const { isAuthenticated, user, logout } = useAuth();

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-brand">
                    🛒 E-Commerce
                </Link>

                <div className="navbar-links">
                    <Link to="/products" className="nav-link">
                        Products
                    </Link>

                    {isAuthenticated ? (
                        <>
                            <Link to="/cart" className="nav-link cart-link">
                                🛒 Cart
                            </Link>
                            <div className="navbar-user">
                                <span className="user-name">👤 {user?.username}</span>
                                <button onClick={logout} className="btn-logout">
                                    Logout
                                </button>
                            </div>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="nav-link">
                                Login
                            </Link>
                            <Link to="/signup" className="btn btn-primary btn-signup">
                                Sign Up
                            </Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

/**
 * Protected Route Component
 * Redirects to login if user is not authenticated
 */
const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner"></div>
                <p>Loading...</p>
            </div>
        );
    }

    return isAuthenticated ? children : <Navigate to="/login" />;
};

/**
 * Home Page Component
 * Landing page with welcome message
 */
const HomePage = () => {
    const { isAuthenticated } = useAuth();

    return (
        <div className="home-page">
            <div className="home-hero">
                <h1>Welcome to E-Commerce Store</h1>
                <p className="home-subtitle">
                    Discover amazing products at great prices
                </p>
                <div className="home-actions">
                    <Link to="/products" className="btn btn-primary btn-large">
                        Browse Products
                    </Link>
                    {!isAuthenticated && (
                        <Link to="/signup" className="btn btn-secondary btn-large">
                            Create Account
                        </Link>
                    )}
                </div>
            </div>

            <div className="home-features">
                <div className="feature-card">
                    <div className="feature-icon">🚀</div>
                    <h3>Fast Delivery</h3>
                    <p>Quick and reliable shipping on all orders</p>
                </div>
                <div className="feature-card">
                    <div className="feature-icon">💳</div>
                    <h3>Secure Payments</h3>
                    <p>Your transactions are safe and encrypted</p>
                </div>
                <div className="feature-card">
                    <div className="feature-icon">⭐</div>
                    <h3>Quality Products</h3>
                    <p>Curated selection of top-rated items</p>
                </div>
            </div>
        </div>
    );
};

/**
 * Main App Component
 */
function App() {
    return (
        <Router>
            <AuthProvider>
                <div className="App">
                    <Navbar />

                    <main className="main-content">
                        <Routes>
                            {/* Public routes */}
                            <Route path="/" element={<HomePage />} />
                            <Route path="/login" element={<Login />} />
                            <Route path="/signup" element={<Signup />} />
                            <Route path="/products" element={<ProductList />} />

                            {/* Protected routes */}
                            <Route
                                path="/cart"
                                element={
                                    <ProtectedRoute>
                                        <ShoppingCart />
                                    </ProtectedRoute>
                                }
                            />

                            {/* Fallback route */}
                            <Route path="*" element={<Navigate to="/" />} />
                        </Routes>
                    </main>

                    <footer className="footer">
                        <p>© 2026 E-Commerce App. Built with Flask & React for DevOps Portfolio.</p>
                    </footer>
                </div>
            </AuthProvider>
        </Router>
    );
}

export default App;
