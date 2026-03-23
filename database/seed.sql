-- Sample Product Data for E-Commerce Application
-- This script populates the products table with sample data for testing

-- Clear existing products (optional - comment out if you want to preserve data)
-- TRUNCATE TABLE products RESTART IDENTITY CASCADE;

-- Electronics Category
INSERT INTO products (name, description, price, stock, category, image_url) VALUES
('Wireless Headphones', 'Premium noise-canceling wireless headphones with 30-hour battery life', 149.99, 50, 'Electronics', 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'),
('Smart Watch', 'Fitness tracker with heart rate monitor and GPS', 299.99, 35, 'Electronics', 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400'),
('Laptop Stand', 'Ergonomic aluminum laptop stand with adjustable height', 49.99, 100, 'Electronics', 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400'),
('Mechanical Keyboard', 'RGB backlit mechanical gaming keyboard with Cherry MX switches', 129.99, 45, 'Electronics', 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400'),
('Wireless Mouse', 'Ergonomic wireless mouse with precision tracking', 39.99, 75, 'Electronics', 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400');

-- Clothing Category
INSERT INTO products (name, description, price, stock, category, image_url) VALUES
('Classic T-Shirt', 'Premium cotton t-shirt in various colors', 24.99, 200, 'Clothing', 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400'),
('Denim Jeans', 'Comfortable slim-fit denim jeans', 59.99, 80, 'Clothing', 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400'),
('Hoodie', 'Cozy pullover hoodie with front pocket', 44.99, 60, 'Clothing', 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400'),
('Running Shoes', 'Lightweight athletic shoes for running and training', 89.99, 55, 'Clothing', 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400');

-- Home & Living Category
INSERT INTO products (name, description, price, stock, category, image_url) VALUES
('Coffee Maker', 'Programmable coffee maker with thermal carafe', 79.99, 40, 'Home & Living', 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=400'),
('Desk Lamp', 'LED desk lamp with adjustable brightness and color temperature', 34.99, 65, 'Home & Living', 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400'),
('Plant Pot Set', 'Set of 3 ceramic plant pots with drainage', 29.99, 90, 'Home & Living', 'https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=400'),
('Throw Blanket', 'Soft fleece throw blanket for couch or bed', 34.99, 70, 'Home & Living', 'https://images.unsplash.com/photo-1544967919-d516f119bef0?w=400');

-- Books Category
INSERT INTO products (name, description, price, stock, category, image_url) VALUES
('Programming Book', 'Complete guide to modern web development', 39.99, 25, 'Books', 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400'),
('Fiction Novel', 'Bestselling mystery thriller', 19.99, 40, 'Books', 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400'),
('Cookbook', 'Healthy recipes for busy professionals', 29.99, 30, 'Books', 'https://images.unsplash.com/photo-1466637574441-749b8f19452f?w=400');

-- Success message
SELECT 'Sample products inserted successfully!' as message;
SELECT COUNT(*) as total_products FROM products;
