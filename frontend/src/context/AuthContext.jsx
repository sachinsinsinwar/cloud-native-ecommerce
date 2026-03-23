/**
 * Authentication Context
 * 
 * Provides global authentication state management using React Context API.
 * This context handles:
 * - User authentication state
 * - Login/logout functionality
 * - Token management
 * - User data persistence
 */

import React, { createContext, useState, useEffect, useContext } from 'react';
import { authAPI } from '../services/api';

// Create context
const AuthContext = createContext({});

/**
 * AuthProvider Component
 * Wraps the application to provide authentication state to all components
 */
export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    /**
     * Check if user is authenticated on component mount
     * This validates the stored token and retrieves user data
     */
    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('token');
            const storedUser = localStorage.getItem('user');

            if (token && storedUser) {
                try {
                    // Verify token is still valid
                    const response = await authAPI.checkAuth();

                    if (response.data.authenticated) {
                        setUser(JSON.parse(storedUser));
                        setIsAuthenticated(true);
                    } else {
                        // Token invalid, clear storage
                        localStorage.removeItem('token');
                        localStorage.removeItem('user');
                    }
                } catch (error) {
                    // Token validation failed, clear storage
                    console.error('Auth check failed:', error);
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                }
            }

            setLoading(false);
        };

        initAuth();
    }, []);

    /**
     * Login function
     * @param {string} username - Username or email
     * @param {string} password - User password
     * @returns {Promise} - Resolves with user data or rejects with error
     */
    const login = async (username, password) => {
        try {
            const response = await authAPI.login({ username, password });
            const { token, user: userData } = response.data;

            // Store token and user data
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(userData));

            // Update state
            setUser(userData);
            setIsAuthenticated(true);

            return userData;
        } catch (error) {
            console.error('Login failed:', error);
            throw error;
        }
    };

    /**
     * Signup function
     * @param {Object} userData - { username, email, password }
     * @returns {Promise} - Resolves with user data or rejects with error
     */
    const signup = async (userData) => {
        try {
            const response = await authAPI.signup(userData);
            const { token, user: newUser } = response.data;

            // Store token and user data
            localStorage.setItem('token', token);
            localStorage.setItem('user', JSON.stringify(newUser));

            // Update state
            setUser(newUser);
            setIsAuthenticated(true);

            return newUser;
        } catch (error) {
            console.error('Signup failed:', error);
            throw error;
        }
    };

    /**
     * Logout function
     * Clears authentication state and stored credentials
     */
    const logout = async () => {
        try {
            await authAPI.logout();
        } catch (error) {
            console.error('Logout API call failed:', error);
        } finally {
            // Clear state and storage regardless of API call result
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setUser(null);
            setIsAuthenticated(false);
        }
    };

    /**
     * Context value object
     * These values/functions are available to all consuming components
     */
    const value = {
        user,
        isAuthenticated,
        loading,
        login,
        signup,
        logout,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

/**
 * Custom hook to use authentication context
 * Usage: const { user, login, logout } = useAuth();
 */
export const useAuth = () => {
    const context = useContext(AuthContext);

    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }

    return context;
};

export default AuthContext;
