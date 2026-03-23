/**
 * Product List Component
 * 
 * Displays a grid of products with filtering, search, and pagination.
 * Integrates with backend API to fetch products and handles caching.
 */

import React, { useState, useEffect } from 'react';
import { productsAPI } from '../../services/api';
import ProductCard from './ProductCard';
import './Products.css';

const ProductList = () => {
    // Product state
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Filter and pagination state
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [page, setPage] = useState(1);
    const [pagination, setPagination] = useState(null);

    /**
     * Fetch products from API
     */
    const fetchProducts = async () => {
        setLoading(true);
        setError('');

        try {
            const params = {
                page,
                per_page: 12,
            };

            // Add filters if selected
            if (selectedCategory) {
                params.category = selectedCategory;
            }
            if (searchQuery) {
                params.search = searchQuery;
            }

            const response = await productsAPI.getProducts(params);
            setProducts(response.data.products);
            setPagination(response.data.pagination);
        } catch (err) {
            setError('Failed to load products. Please try again.');
            console.error('Error fetching products:', err);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Fetch categories from API
     */
    const fetchCategories = async () => {
        try {
            const response = await productsAPI.getCategories();
            setCategories(response.data.categories);
        } catch (err) {
            console.error('Error fetching categories:', err);
        }
    };

    /**
     * Initial data load
     */
    useEffect(() => {
        fetchCategories();
    }, []);

    /**
     * Fetch products when filters or page changes
     */
    useEffect(() => {
        fetchProducts();
    }, [page, selectedCategory, searchQuery]);

    /**
     * Handle search input
     */
    const handleSearch = (e) => {
        setSearchQuery(e.target.value);
        setPage(1); // Reset to first page on search
    };

    /**
     * Handle category selection
     */
    const handleCategoryChange = (category) => {
        setSelectedCategory(category);
        setPage(1); // Reset to first page on category change
    };

    /**
     * Clear all filters
     */
    const clearFilters = () => {
        setSelectedCategory('');
        setSearchQuery('');
        setPage(1);
    };

    return (
        <div className="products-container">
            {/* Header */}
            <div className="products-header">
                <h1>Our Products</h1>
                <p className="products-subtitle">Discover amazing products at great prices</p>
            </div>

            {/* Filters and Search */}
            <div className="products-filters">
                {/* Search bar */}
                <div className="search-bar">
                    <input
                        type="text"
                        placeholder="Search products..."
                        value={searchQuery}
                        onChange={handleSearch}
                        className="search-input"
                    />
                </div>

                {/* Category filter */}
                <div className="category-filters">
                    <button
                        className={`category-btn ${!selectedCategory ? 'active' : ''}`}
                        onClick={() => handleCategoryChange('')}
                    >
                        All Categories
                    </button>
                    {categories.map((category) => (
                        <button
                            key={category}
                            className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
                            onClick={() => handleCategoryChange(category)}
                        >
                            {category}
                        </button>
                    ))}
                </div>

                {/* Active filters */}
                {(selectedCategory || searchQuery) && (
                    <div className="active-filters">
                        <span>Filters: </span>
                        {selectedCategory && <span className="filter-tag">{selectedCategory}</span>}
                        {searchQuery && <span className="filter-tag">"{searchQuery}"</span>}
                        <button className="clear-filters-btn" onClick={clearFilters}>
                            Clear all
                        </button>
                    </div>
                )}
            </div>

            {/* Error message */}
            {error && (
                <div className="error-banner">
                    {error}
                    <button onClick={fetchProducts} className="retry-btn">
                        Retry
                    </button>
                </div>
            )}

            {/* Loading state */}
            {loading && (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading products...</p>
                </div>
            )}

            {/* Products grid */}
            {!loading && !error && (
                <>
                    {products.length > 0 ? (
                        <div className="products-grid">
                            {products.map((product) => (
                                <ProductCard
                                    key={product.id}
                                    product={product}
                                    onAddToCart={fetchProducts}
                                />
                            ))}
                        </div>
                    ) : (
                        <div className="no-products">
                            <p>No products found</p>
                            {(selectedCategory || searchQuery) && (
                                <button onClick={clearFilters} className="btn btn-primary">
                                    Clear Filters
                                </button>
                            )}
                        </div>
                    )}

                    {/* Pagination */}
                    {pagination && pagination.total_pages > 1 && (
                        <div className="pagination">
                            <button
                                className="pagination-btn"
                                onClick={() => setPage(page - 1)}
                                disabled={!pagination.has_prev}
                            >
                                Previous
                            </button>

                            <span className="pagination-info">
                                Page {pagination.page} of {pagination.total_pages}
                            </span>

                            <button
                                className="pagination-btn"
                                onClick={() => setPage(page + 1)}
                                disabled={!pagination.has_next}
                            >
                                Next
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
};

export default ProductList;
