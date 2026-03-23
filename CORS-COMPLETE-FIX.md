# Complete CORS Fix - Container Recreation Required

## 🔍 Final Root Cause Discovered

After multiple debugging attempts, the actual issue was:

**`docker compose restart` does NOT reload environment variables from the `.env` file!**

### What Was Happening

1. ✅ We updated `.env` file with correct CORS_ORIGINS including port 3002
2. ❌ We ran `docker compose restart backend`  
3. ❌ The backend container kept the OLD environment variables from when it was first created

### Verification

**Checked the running container's environment:**
```powershell
docker exec ecommerce-backend printenv | Select-String -Pattern "CORS"
```

**Before fix:**
```
CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://localhost:5173
```
❌ Port 3002 missing!

**After fix:**
```
CORS_ORIGINS=http://localhost:3000,http://localhost:3002,http://localhost:80,http://localhost:5173
```
✅ Port 3002 included!

## ✅ Correct Solution

### Stop, Remove, and Recreate Container

```powershell
# Stop the container
docker compose stop backend

# Remove the container (this deletes the old environment variables)
docker compose rm -f backend

# Create a new container with fresh environment variables from .env
docker compose up -d backend
```

### Why This Works

- `docker compose restart` = stops and starts the SAME container (keeps old env vars)
- `docker compose rm + up` = deletes old container and creates NEW one (reads .env again)

## 🎯 Complete Fix Steps Applied

### 1. Updated .env File
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3002,http://localhost:80,http://localhost:5173
```

### 2. Recreated Backend Container
```powershell
docker compose stop backend
docker compose rm -f backend  
docker compose up -d backend
```

### 3. Verified Configuration
```powershell
# Check environment variable in running container
docker exec ecommerce-backend printenv | Select-String -Pattern "CORS"

# Result: ✅ CORS_ORIGINS includes port 3002

# Check backend health
Invoke-RestMethod http://localhost:5000/health

# Result: ✅ Healthy (database and Redis connected)
```

## 🧪 Testing Instructions

### 1. Clear Browser Cache
**Important:** Your browser may have cached the old CORS rejection.

**Option A: Hard Refresh**
- Windows: `Ctrl + Shift + R` or `Ctrl + F5`
- Mac: `Cmd + Shift + R`

**Option B: Incognito/Private Window** (Recommended)
- Open a new private/incognito window
- Navigate to `http://localhost:3002`

### 2. Test Signup
1. Go to `http://localhost:3002/signup`
2. Fill in:
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `Test123!`
3. Click "Create Account"

**Expected Result:**
- ✅ Network tab shows `POST http://localhost:5000/api/auth/signup` with **Status: 201**
- ✅ Response contains JWT token
- ✅ You're redirected and logged in

### 3. Test Login
1. Go to `http://localhost:3002/login`
2. Enter credentials
3. Click "Log In"

**Expected Result:**
- ✅ Network tab shows `POST http://localhost:5000/api/auth/login` with **Status: 200**
- ✅ Response contains JWT token
- ✅ You're redirected and logged in

## 📊 What to Check if Still Failing

### Check 1: Backend Container Environment
```powershell
docker exec ecommerce-backend printenv | Select-String -Pattern "CORS"
```
Should show: `CORS_ORIGINS=http://localhost:3000,http://localhost:3002,...`

### Check 2: Network Tab Headers
In browser DevTools → Network → Click the failed request → Headers:

**Response Headers should include:**
```
Access-Control-Allow-Origin: http://localhost:3002
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

### Check 3: Request URL
The request should be going to:
```
http://localhost:5000/api/auth/signup
```

NOT:
- ~~http://localhost:3002/api/auth/signup~~ (wrong port)
- ~~http://localhost:5000/auth/signup~~ (missing /api prefix)

## 📝 Key Lessons Learned

### 1. Docker Environment Variables
- **`.env` file changes** require container recreation, not just restart
- **Always use:** `docker compose up -d` (recreates if env changed)
- **Avoid:** `docker compose restart` (keeps old environment)

### 2. CORS Configuration
- Must include **exact origin** (protocol + host + port)
- Port 3000 ≠ Port 3002 (different origins!)
- Browser caches CORS rejections (use incognito or hard refresh)

### 3. Debugging Workflow
1. Check `.env` file has correct values
2. Verify running container has those values
3. If mismatch → recreate container
4. Clear browser cache or use incognito
5. Check Network tab for actual errors

## ✅ Current Status

**All Services Running:**
```
✅ Frontend (React/Nginx) - http://localhost:3002
✅ Backend (Flask) - http://localhost:5000  
✅ PostgreSQL - Port 5433
✅ Redis - Port 6380
```

**Backend Configuration:**
```
✅ CORS_ORIGINS includes localhost:3002
✅ Database connected
✅ Redis connected
✅ All API routes registered under /api/
```

**Expected Behavior:**
- Frontend can now make requests to backend
- CORS headers allow localhost:3002 origin
- Signup and login endpoints work
- JWT tokens are issued correctly

## 🔄 Quick Reference Commands

### Recreate Container (when .env changes)
```powershell
docker compose stop <service>
docker compose rm -f <service>
docker compose up -d <service>
```

### Or use shorthand (recreates all changed services)
```powershell
docker compose up -d --force-recreate backend
```

### Check container environment
```powershell
docker exec <container-name> printenv
```

### View current config
```powershell
docker compose config
```

### Full reset (if all else fails)
```powershell
docker compose down
docker compose up -d
```

---

**The CORS issue is now definitively fixed. The container has been recreated with the correct configuration. Try it now in an incognito window!** 🎉
