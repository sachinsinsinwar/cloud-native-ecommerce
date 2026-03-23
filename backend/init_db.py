"""
Initialize SQLite database with sample data

Run this script to create the database and populate it with sample products.
"""

from app import create_app
from models import db, User, Product

# Create app and database
app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Database tables created!")
    
    # Check if we already have products
    if Product.query.count() > 0:
        print(f"✅ Database already has {Product.query.count()} products")
        exit(0)
    
    # Add sample products
    products = [
        # Electronics
        Product(name='Wireless Headphones', description='Premium noise-canceling wireless headphones with 30-hour battery life', price=149.99,stock=50, category='Electronics', image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400'),
        Product(name='Smart Watch', description='Fitness tracker with heart rate monitor and GPS', price=299.99, stock=35, category='Electronics', image_url='https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400'),
        Product(name='Laptop Stand', description='Ergonomic aluminum laptop stand with adjustable height', price=49.99, stock=100, category='Electronics', image_url='https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400'),
        Product(name='Mechanical Keyboard', description='RGB backlit mechanical gaming keyboard with Cherry MX switches', price=129.99, stock=45, category='Electronics', image_url='https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400'),
        Product(name='Wireless Mouse', description='Ergonomic wireless mouse with precision tracking', price=39.99, stock=75, category='Electronics', image_url='https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400'),
        
        # Clothing
        Product(name='Classic T-Shirt', description='Premium cotton t-shirt in various colors', price=24.99, stock=200, category='Clothing', image_url='https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400'),
        Product(name='Denim Jeans', description='Comfortable slim-fit denim jeans', price=59.99, stock=80, category='Clothing', image_url='https://images.unsplash.com/photo-1542272604-787c3835535d?w=400'),
        Product(name='Hoodie', description='Cozy pullover hoodie with front pocket', price=44.99, stock=60, category='Clothing', image_url='https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400'),
        Product(name='Running Shoes', description='Lightweight athletic shoes for running and training', price=89.99, stock=55, category='Clothing', image_url='https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400'),
        
        # Home & Living
        Product(name='Coffee Maker', description='Programmable coffee maker with thermal carafe', price=79.99, stock=40, category='Home & Living', image_url='https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=400'),
        Product(name='Desk Lamp', description='LED desk lamp with adjustable brightness and color temperature', price=34.99, stock=65, category='Home & Living', image_url='https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400'),
        Product(name='Plant Pot Set', description='Set of 3 ceramic plant pots with drainage', price=29.99, stock=90, category='Home & Living', image_url='https://images.unsplash.com/photo-1485955900006-10f4d324d411?w=400'),
        Product(name='Throw Blanket', description='Soft fleece throw blanket for couch or bed', price=34.99, stock=70, category='Home & Living', image_url='https://images.unsplash.com/photo-1544967919-d516f119bef0?w=400'),
        
        # Books
        Product(name='Programming Book', description='Complete guide to modern web development', price=39.99, stock=25, category='Books', image_url='https://images.unsplash.com/photo-1532012197267-da84d127e765?w=400'),
        Product(name='Fiction Novel', description='Bestselling mystery thriller', price=19.99, stock=40, category='Books', image_url='https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400'),
        Product(name='Cookbook', description='Healthy recipes for busy professionals', price=29.99, stock=30, category='Books', image_url='https://images.unsplash.com/photo-1466637574441-749b8f19452f?w=400'),
    ]
    
    for product in products:
        db.session.add(product)
    
    db.session.commit()
    print(f"✅ Added {len(products)} sample products to the database!")
    print("✅ Database initialization complete!")
