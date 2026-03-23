"""
Database Models Module

This module defines SQLAlchemy models for the e-commerce application.
Models include User, Product, Cart, CartItem, Order, and OrderItem.
Each model represents a table in the PostgreSQL database with defined relationships.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

# Initialize SQLAlchemy instance (will be bound to Flask app in app.py)
db = SQLAlchemy()


class User(db.Model):
    """
    User model for authentication and user management
    
    Relationships:
    - One user can have one cart
    - One user can have multiple orders
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    cart = db.relationship('Cart', backref='user', uselist=False, lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password using bcrypt"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convert user object to dictionary (excluding password)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Product(db.Model):
    """
    Product model for storing product information
    
    Relationships:
    - Products can be in multiple cart items
    - Products can be in multiple order items
    """
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Decimal for precise currency values
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(100), nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    
    def to_dict(self):
        """Convert product object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),  # Convert Decimal to float for JSON serialization
            'stock': self.stock,
            'image_url': self.image_url,
            'category': self.category,
            'created_at': self.created_at.isoformat()
        }


class Cart(db.Model):
    """
    Shopping cart model - each user has one cart
    
    Relationships:
    - One cart belongs to one user
    - One cart can have multiple cart items
    """
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('CartItem', backref='cart', lazy=True, cascade='all, delete-orphan')
    
    def get_total(self):
        """Calculate total price of all items in cart"""
        return sum(item.product.price * item.quantity for item in self.items)
    
    def to_dict(self):
        """Convert cart object to dictionary with items"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'items': [item.to_dict() for item in self.items],
            'total': float(self.get_total()),
            'created_at': self.created_at.isoformat()
        }


class CartItem(db.Model):
    """
    Cart item model - represents a product in a user's cart with quantity
    
    Relationships:
    - Each cart item belongs to one cart
    - Each cart item references one product
    """
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    # Ensure a product can only appear once per cart
    __table_args__ = (db.UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),)
    
    def to_dict(self):
        """Convert cart item to dictionary"""
        return {
            'id': self.id,
            'product': self.product.to_dict(),
            'quantity': self.quantity,
            'subtotal': float(self.product.price * self.quantity)
        }


class Order(db.Model):
    """
    Order model - created when user checks out their cart
    
    Relationships:
    - Each order belongs to one user
    - Each order has multiple order items
    """
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, processing, shipped, delivered, cancelled
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert order object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat()
        }


class OrderItem(db.Model):
    """
    Order item model - represents a product in an order
    Stores price at time of purchase for historical accuracy
    
    Relationships:
    - Each order item belongs to one order
    - Each order item references one product
    """
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Store price at purchase time
    
    def to_dict(self):
        """Convert order item to dictionary"""
        return {
            'id': self.id,
            'product': self.product.to_dict(),
            'quantity': self.quantity,
            'price': float(self.price),
            'subtotal': float(self.price * self.quantity)
        }
