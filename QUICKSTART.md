# Quick Start Guide - Running Servers Locally

## 🎯 Folder Structure Benefits

Your project follows this industry-standard structure:

```
backend/          → Flask API (Python)
  routes/         → API endpoints organized by feature
  utils/          → Reusable utilities (auth, caching)
  models.py       → Database models in one place
  config.py       → Environment configuration
  
frontend/         → React App (JavaScript)
  src/
    components/   → UI components by feature
    context/      → Global state management
    services/     → API communication layer
    
database/         → SQL scripts for schema & data
docker-compose.yml → One-command deployment
```

**Why This Structure?**
✅ **Separation of Concerns**: Each file has one clear purpose
✅ **Scalability**: Easy to add new features without conflicts
✅ **Team Collaboration**: Multiple developers can work independently
✅ **Testing**: Can test each module separately
✅ **Deployment**: Clear separation for containerization

---

## 🚀 Running Locally - Manual Setup

### Prerequisites Check

```powershell
# Check Python
python --version  # Need 3.9+

# Check Node.js
node --version    # Need 18+

# Check PostgreSQL
psql --version    # Need 14+
```

### Step 1: Start  PostgreSQL & Redis

**Option A: Using Docker for just DB+Redis**
```powershell
# Start only database and cache (not the apps)
docker run -d --name pg-local -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:14-alpine
docker run -d --name redis-local -p 6379:6379 redis:7-alpine

# Initialize database
docker exec -i pg-local psql -U postgres < database/init.sql
docker exec -i pg-local psql -U postgres -d ecommerce_db < database/seed.sql
```

**Option B: Local PostgreSQL/Redis**
If you have PostgreSQL and Redis installed locally:
```powershell
# Start PostgreSQL service (if not running)
# Windows: services.msc → PostgreSQL service → Start

# Start Redis service (if not running)
# Windows: redis-server

# Initialize database
psql -U postgres -f database/init.sql
psql -U postgres -d ecommerce_db -f database/seed.sql
```

### Step 2: Start Backend (Flask)

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

✅ Backend will run on: **http://localhost:5000**

### Step 3: Start Frontend (React)

Open a **NEW terminal** (keep backend running):

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

✅ Frontend will run on: **http://localhost:3000**

### Step 4: Test the Application

1. Open browser: **http://localhost:3000**
2. Create account → Browse products → Add to cart → Checkout

---

## 🐛 Common Issues

### Port Already in Use

```powershell
# Find what's using the port
netstat -ano | findstr ":5000"

# Kill the process (replace PID)
taskkill /PID <process_id> /F
```

### Database Connection Error

Check PostgreSQL is running and connection string in backend/config.py:
```python
DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/ecommerce_db'
```

### Redis Connection Error

Backend will work without Redis (caching just won't work). To fix:
- Start Redis: `redis-server`
- Or update `REDIS_URL` in backend/config.py

---

## 📊 What's Running?

| Service    | URL                        | Purpose                      |
|------------|----------------------------|------------------------------|
| Frontend   | http://localhost:3000      | React UI                     |
| Backend    | http://localhost:5000      | Flask API                    |
| Health     | http://localhost:5000/health | Check backend status         |
| PostgreSQL | localhost:5432             | Database                     |
| Redis      | localhost:6379             | Cache                        |

---

## 🎓 Understanding the Structure

### Backend Organization

```
backend/routes/
  auth.py      → signup, login, logout
  products.py  → list products, get product, create product
  cart.py      → add to cart, update cart, checkout
```

**Why separate routes?**
- Each file handles one domain (auth, products, cart)
- Easy to find and fix bugs
- Can test each module independently
- Team members can work on different routes simultaneously

### Frontend Organization

```
frontend/src/components/
  Auth/        → Login.jsx, Signup.jsx (authentication UI)
  Products/    → ProductList.jsx, ProductCard.jsx (product display)
  Cart/        → ShoppingCart.jsx (cart management)
```

**Why component-based?**
- Reusable UI pieces
- Each component has its own styles
- Easy to update UI without breaking other parts
- Clear separation between features

---

## 💡 Next Steps

1. **Development**: Make changes to code and see live updates
2. **Add Features**: Create new route files or components
3. **Deploy**: Use `docker-compose up` for production deployment
4. **Scale**: Each service can scale independently
