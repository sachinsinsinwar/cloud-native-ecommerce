"""
Flask Application Factory

This is the main Flask application factory that:
1. Creates and configures the Flask app
2. Initializes database and Redis connections
3. Registers blueprints for different API routes
4. Sets up CORS for frontend communication
5. Provides health check and basic error handling
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from models import db
from utils.cache import cache

def create_app(config_name=None):
    """
    Application factory function
    
    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
                          Defaults to FLASK_ENV environment variable or 'development'
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    
    # Configure CORS - allows frontend to make requests to backend
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(cart_bp)
    
    # Create database tables (in production, use migrations instead)
    with app.app_context():
        db.create_all()
        app.logger.info('Database tables created/verified')
    
    # Root endpoint - API information
    @app.route('/')
    def index():
        """API root endpoint with available routes information"""
        return jsonify({
            'name': 'E-Commerce API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'auth': '/api/auth',
                'products': '/api/products',
                'cart': '/api/cart',
                'health': '/health'
            },
            'documentation': 'See README.md for API documentation'
        }), 200
    
    # Health check endpoint - useful for DevOps monitoring
    @app.route('/health')
    def health_check():
        """
        Health check endpoint for monitoring
        
        Checks:
        - Application is running
        - Database connection
        - Redis connection
        
        Returns:
            200: All systems operational
            503: One or more systems down
        """
        health_status = {
            'status': 'healthy',
            'checks': {}
        }
        
        # Check database connection
        try:
            db.session.execute(db.text('SELECT 1'))
            health_status['checks']['database'] = 'connected'
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['checks']['database'] = f'error: {str(e)}'
        
        # Check Redis connection
        try:
            if cache.redis_client:
                cache.redis_client.ping()
                health_status['checks']['redis'] = 'connected'
            else:
                health_status['checks']['redis'] = 'not configured'
        except Exception as e:
            health_status['status'] = 'degraded'  # Redis failure is not critical
            health_status['checks']['redis'] = f'error: {str(e)}'
        
        status_code = 200 if health_status['status'] == 'healthy' else 503
        return jsonify(health_status), status_code
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        db.session.rollback()  # Rollback any pending transactions
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors (method not allowed)"""
        return jsonify({'error': 'Method not allowed'}), 405
    
    app.logger.info(f'Flask app created with config: {config_name}')
    
    return app


# Create app instance for running with gunicorn or flask run
app = create_app()

if __name__ == '__main__':
    """
    Run the application in development mode
    
    For production, use a production server like gunicorn:
        gunicorn -w 4 -b 0.0.0.0:5001 app:app
    """
    # Use port 5001 to avoid conflicts with existing services
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
