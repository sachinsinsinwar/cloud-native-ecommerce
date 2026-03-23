# E-Commerce Application

A full-stack e-commerce application built with Flask (Python) backend, React frontend, PostgreSQL database, and Redis caching. Perfect for DevOps portfolio projects with complete Docker containerization.

## 🚀 Features

### Backend (Flask/Python)
- **User Authentication**: JWT-based signup/login with password hashing
- **Product Management**: RESTful API for product listing, details, and creation
- **Shopping Cart**: Add/update/remove items with stock validation
- **Order Processing**: Checkout functionality with inventory management
- **Redis Caching**: Product data caching for improved performance
- **Health Checks**: Monitoring endpoints for database and Redis connectivity

### Frontend (React)
- **User Interface**: Modern, responsive design with React 18
- **Authentication Pages**: Login and signup with form validation
- **Product Catalog**: Grid view with search, filtering, and pagination
- **Shopping Cart**: Full cart management with quantity controls
- **Protected Routes**: Authentication-based access control

### Database (PostgreSQL)
- Users, Products, Carts, Orders, and Order Items tables
- Proper relationships and constraints
- Sample seed data included

### Caching (Redis)
- Session management
- Product data caching with TTL
- Cache invalidation on updates

## 📋 Prerequisites

- **Docker** and **Docker Compose** (recommended)
- OR:
  - Python 3.9+
  - Node.js 18+
  - PostgreSQL 14+
  - Redis 7+

## 🐳 Quick Start with Docker

1. **Clone the repository**
   ```bash
   cd "DevOps with AI Antigravity"
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Health Check: http://localhost:5000/health

4. **Stop services**
   ```bash
   docker-compose down
   ```

## 💻 Manual Setup (Without Docker)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp ../.env.example .env
   # Edit .env with your database and Redis credentials
   ```

5. **Initialize database**
   ```bash
   # Make sure PostgreSQL is running
   psql -U postgres -f ../database/init.sql
   psql -U postgres -d ecommerce_db -f ../database/seed.sql
   ```

6. **Run the backend**
   ```bash
   python app.py
   # Backend will run on http://localhost:5000
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "VITE_API_URL=http://localhost:5000" > .env
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   # Frontend will run on http://localhost:3000
   ```

## 📚 API Documentation

### Authentication Endpoints

- **POST** `/api/auth/signup` - Register new user
- **POST** `/api/auth/login` - Login user
- **POST** `/api/auth/logout` - Logout user
- **GET** `/api/auth/me` - Get current user info

### Product Endpoints

- **GET** `/api/products` - List all products (with pagination, search, filter)
- **GET** `/api/products/:id` - Get product details
- **POST** `/api/products` - Create new product
- **GET** `/api/products/categories` - Get all categories

### Cart Endpoints

- **GET** `/api/cart` - Get user's cart
- **POST** `/api/cart/items` - Add item to cart
- **PUT** `/api/cart/items/:id` - Update cart item quantity
- **DELETE** `/api/cart/items/:id` - Remove item from cart
- **POST** `/api/cart/checkout` - Create order from cart
- **POST** `/api/cart/clear` - Clear cart

### Example API Calls

**Signup:**
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"password123"}'
```

**Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john","password":"password123"}'
```

**Get Products:**
```bash
curl http://localhost:5000/api/products
```

## 🗂️ Project Structure

```
.
├── backend/                    # Flask backend
│   ├── app.py                 # Main application factory
│   ├── config.py              # Configuration management
│   ├── models.py              # Database models
│   ├── requirements.txt       # Python dependencies
│   ├── routes/                # API routes
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── products.py       # Product endpoints
│   │   └── cart.py           # Cart endpoints
│   └── utils/                 # Utilities
│       ├── auth_middleware.py # JWT authentication
│       └── cache.py           # Redis caching
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.jsx            # Main app component
│   │   ├── components/        # React components
│   │   │   ├── Auth/         # Login/Signup
│   │   │   ├── Products/     # Product list/card
│   │   │   └── Cart/         # Shopping cart
│   │   ├── context/          # React context
│   │   │   └── AuthContext.jsx
│   │   └── services/         # API service
│   │       └── api.js
│   ├── package.json
│   └── vite.config.js
│
├── database/                   # Database scripts
│   ├── init.sql              # Schema creation
│   └── seed.sql              # Sample data
│
├── docker-compose.yml         # Docker orchestration
└── README.md                  # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory (copy from `.env.example`):

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecommerce_db
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=http://localhost:3000
VITE_API_URL=http://localhost:5000
```

### Docker Configuration

The `docker-compose.yml` file includes:
- PostgreSQL with automatic schema initialization
- Redis for caching
- Flask backend with hot-reload
- React frontend with Vite dev server

## 🧪 Testing

### Backend Health Check
```bash
curl http://localhost:5000/health
```

### Test User Flow
1. Create an account at `/signup`
2. Login at `/login`
3. Browse products at `/products`
4. Add items to cart
5. View cart at `/cart`
6. Checkout to create an order

## 🛠️ Development

### Adding New Products

Use the API or directly insert into the database:

```bash
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Product",
    "description": "Product description",
    "price": 99.99,
    "stock": 50,
    "category": "Electronics",
    "image_url": "https://example.com/image.jpg"
  }'
```

### Redis Cache Management

Check cached data:
```bash
docker exec -it ecommerce-redis redis-cli
KEYS *
GET product:1
```

Clear cache:
```bash
docker exec -it ecommerce-redis redis-cli FLUSHDB
```

## 🚀 Production Deployment

For production:

1. **Update environment variables**
   - Set strong `SECRET_KEY`
   - Configure production database URL
   - Update `CORS_ORIGINS` to your domain

2. **Build frontend for production**
   ```bash
   cd frontend
   npm run build
   ```

3. **Use production server for backend**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Use Docker production builds**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 📝 License

This project is created for educational and portfolio purposes.

## 👤 Author

Built as a DevOps portfolio project demonstrating full-stack development with containerization.

## 🤝 Contributing

This is a portfolio project, but suggestions and improvements are welcome!
