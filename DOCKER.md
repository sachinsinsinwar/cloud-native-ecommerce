# =============================================================================
# Docker Containerization Guide
# Complete reference for containerizing the e-commerce application
# =============================================================================

## 📦 Overview

This guide explains the complete Docker containerization strategy for the e-commerce application with 4 services:

1. **Flask Backend** (Python 3.9) - RESTful API
2. **React Frontend** (Node 16) - User Interface  
3. **PostgreSQL** (v14) - Relational Database
4. **Redis** (v7) - In-memory Cache

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                          │
│  (ecommerce-network - 172.25.0.0/16)                       │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Frontend   │───▶│   Backend    │───▶│  PostgreSQL  │ │
│  │  (nginx:80)  │    │ (Flask:5000) │    │   (:5432)    │ │
│  │   Node 16    │    │  Python 3.9  │    │   Alpine     │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                             │
│         │                    │            ┌──────────────┐ │
│         │                    └───────────▶│    Redis     │ │
│         │                                 │   (:6379)    │ │
│         │                                 │   Alpine     │ │
│         │                                 └──────────────┘ │
│         │                                                  │
│  ┌──────▼───────────────────────────────────────────────┐ │
│  │           Persistent Volumes                         │ │
│  │  • postgres_data  • redis_data                       │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Dockerfile Explanations

### 1. Flask Backend Dockerfile

**Location**: `backend/Dockerfile`

#### Base Image Selection
```dockerfile
FROM python:3.9-slim AS builder
```

**Reasoning**:
- ✅ **python:3.9-slim** (~150MB) vs python:3.9 (~900MB) - 83% smaller
- ✅ Debian-based for compatibility
- ✅ Includes essential build tools
- ✅ Regular security updates from official Python team
- ✅ Python 3.9 LTS support until October 2025

#### Multi-Stage Build Strategy
```
Stage 1 (builder): Install dependencies with build tools
Stage 2 (runtime): Copy only what's needed, exclude build tools
Result: Smaller final image, reduced attack surface
```

#### Security Best Practices
1. **Non-root User**
   ```dockerfile
   RUN groupadd -r flaskuser && useradd -r -g flaskuser flaskuser
   USER flaskuser
   ```
   - Prevents privilege escalation attacks
   - Limits container capabilities

2. **Minimal Dependencies**
   ```dockerfile
   RUN apt-get update && apt-get install -y --no-install-recommends
   ```
   - Only install what's absolutely necessary
   - Reduces attack surface

3. **No Cache**
   ```dockerfile
   RUN rm -rf /var/lib/apt/lists/*
   ```
   - Smaller image size
   - No stale package metadata

4. **Health Checks**
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=10s
   ```
   - Docker monitors container health
   - Auto-restart unhealthy containers

#### Essential Build Steps
1. Create non-root user
2. Install system dependencies (PostgreSQL client, gcc)
3. Copy and install Python requirements
4. Copy application code
5. Set environment variables
6. Configure health check
7. Use Gunicorn for production (not Flask dev server)

#### Required Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@postgres:5432/db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-minimum-32-chars
FLASK_ENV=production|development
CORS_ORIGINS=http://localhost:3000
```

---

### 2. React Frontend Dockerfile

**Location**: `frontend/Dockerfile`

#### Base Image Selection
```dockerfile
FROM node:16-alpine AS development
```

**Reasoning**:
- ✅ **node:16-alpine** (~40MB) vs node:16 (~900MB) - 95% smaller
- ✅ Alpine Linux: minimal, security-focused
- ✅ Node 16 LTS: Long-term support until April 2024
- ✅ Fast package installation with apk

#### Multi-Stage Build (3 Stages)

**Stage 1: Development**
```dockerfile
TARGET: development
PURPOSE: Hot-reload for local development
RUNS: Vite dev server on port 3000
```

**Stage 2: Builder**
```dockerfile
TARGET: builder  
PURPOSE: Build optimized production bundle
OUTPUT: Static files in /app/dist
```

**Stage 3: Production**
```dockerfile
TARGET: production
PURPOSE: Serve static files with nginx
RUNS: nginx on port 80
SIZE: ~25MB (just nginx + static files)
```

#### Security Best Practices
1. **Multi-stage removes dev dependencies**
   - Dev dependencies not in final image
   - Only production build artifacts

2. **Nginx as non-root**
   ```dockerfile
   USER nginx
   ```

3. **Security Headers**
   ```nginx
   X-Frame-Options "SAMEORIGIN"
   X-Content-Type-Options "nosniff"
   X-XSS-Protection "1; mode=block"
   ```

4. **SPA Routing Support**
   ```nginx
   try_files $uri $uri/ /index.html;
   ```
   - All routes serve index.html
   - React Router handles client-side routing

#### Build Arguments
```bash
VITE_API_URL: Backend API endpoint (injected at build time)

# Development
docker build --target development -t frontend:dev .

# Production
docker build --target production \
  --build-arg VITE_API_URL=https://api.example.com \
  -t frontend:prod .
```

---

### 3. PostgreSQL Configuration

**Image**: `postgres:14-alpine`

#### Why PostgreSQL 14 Alpine?
- ✅ Official PostgreSQL image with Alpine base
- ✅ PostgreSQL 14: Stable LTS with modern features
- ✅ Alpine: ~200MB vs ~350MB Debian variant
- ✅ Includes pg_isready for health checks

#### Initialization Scripts
```
database/
├── init.sql  → Creates schema (users, products, carts, orders)
└── seed.sql  → Inserts 16 sample products
```

**Execution Order**: Scripts run alphabetically on first start
- `01-init.sql` - Schema creation
- `02-seed.sql` - Sample data

#### Volume Persistence
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```
- Data survives container restarts/removals
- Named volume managed by Docker

#### Security Configuration
```yaml
POSTGRES_HOST_AUTH_METHOD: md5  # Password authentication
POSTGRES_INITDB_ARGS: "-E UTF8"  # UTF-8 encoding
```

#### Performance Tuning
```yaml
resources:
  limits:
    cpus: '1.0'
    memory: 512M
```

---

### 4. Redis Configuration

**Image**: `redis:7-alpine`

#### Why Redis 7 Alpine?
- ✅ Latest stable Redis with performance improvements
- ✅ Alpine base: ~30MB total size
- ✅ Built-in persistence support (AOF/RDB)

#### Configuration
```bash
--appendonly yes           # Enable persistence
--appendfsync everysec     # Sync to disk every second
--maxmemory 256mb          # Memory limit
--maxmemory-policy allkeys-lru  # Eviction strategy
```

#### Persistence Strategy
- **AOF (Append Only File)**: Logs every write operation
- **everysec**: Balance between performance and durability
- **LRU**: Evict least recently used keys when memory full

#### Security
```yaml
--requirepass ${REDIS_PASSWORD}  # Password protection
```

---

## 🚀 Usage Guide

### Quick Start

```bash
# 1. Clone environment template
cp .env.docker .env

# 2. Edit .env and set your passwords
nano .env

# 3. Start all services
docker-compose up --build

# 4. Access application
# Frontend: http://localhost:3000
# Backend:  http://localhost:5000
# Health:   http://localhost:5000/health
```

### Development Mode

```bash
# Start with hot-reload
docker-compose up

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart single service
docker-compose restart backend

# Shell into container
docker-compose exec backend /bin/sh
docker-compose exec postgres psql -U postgres -d ecommerce_db
```

### Production Deployment

```bash
# 1. Set production environment
export FLASK_ENV=production
export FRONTEND_BUILD_TARGET=production

# 2. Build images
docker-compose build --no-cache

# 3. Start in detached mode
docker-compose up -d

# 4. View status
docker-compose ps

# 5. Monitor logs
docker-compose logs -f --tail=100
```

### Useful Commands

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Scale backend instances
docker-compose up -d --scale backend=3

# Check resource usage
docker stats

# Inspect network
docker network inspect devopswithaiantigravity_ecommerce-network

# View volumes
docker volume ls
docker volume inspect devopswithaiantigravity_postgres_data
```

---

## 🔒 Security Checklist

### Before Production Deployment

- [ ] Change all default passwords in `.env`
- [ ] Generate strong SECRET_KEY (32+ random chars)
- [ ] Use secrets management (AWS Secrets, Vault)
- [ ] Enable SSL/TLS certificates
- [ ] Restrict CORS_ORIGINS to your domain only
- [ ] Don't expose PostgreSQL/Redis ports to host
- [ ] Use managed DB services (RDS, Cloud SQL)
- [ ] Enable database backups
- [ ] Configure firewall rules (only 80/443 exposed)
- [ ] Set up logging and monitoring
- [ ] Scan images for vulnerabilities (`docker scan`)
- [ ] Use image digests instead of tags
- [ ] Implement rate limiting
- [ ] Enable container security scanning in CI/CD

---

## 📊 Resource Optimization

### Recommended Limits

| Service    | CPU  | Memory | Purpose                    |
|------------|------|--------|----------------------------|
| PostgreSQL | 1.0  | 512M   | Database operations        |
| Redis      | 0.5  | 256M   | Caching                    |
| Backend    | 1.0  | 512M   | API processing             |
| Frontend   | 0.5  | 256M   | Static file serving        |

### Monitoring

```bash
# Real-time stats
docker stats

# Check health
docker-compose ps
docker inspect --format='{{.State.Health.Status}}' ecommerce-backend
```

---

## 🧪 Testing

### Verify Services

```bash
# Backend health
curl http://localhost:5000/health

# Get products
curl http://localhost:5000/api/products

# Frontend
curl http://localhost:3000

# PostgreSQL
docker-compose exec postgres psql -U postgres -d ecommerce_db -c "SELECT COUNT(*) FROM products;"

# Redis
docker-compose exec redis redis-cli ping
docker-compose exec redis redis-cli KEYS '*'
```

---

## 🛠️ Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Check what's using the port
netstat -ano | findstr :5000

# Change port in .env
BACKEND_PORT=5001
```

**2. Database connection refused**
```bash
# Check if PostgreSQL is ready
docker-compose logs postgres

# Verify health
docker-compose ps

# Wait for health check to pass
```

**3. Redis connection error**
```bash
# Check Redis is running
docker-compose exec redis redis-cli ping

# Verify password (if set)
docker-compose exec redis redis-cli -a yourpassword ping
```

**4. Build failures**
```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

**5. Permission denied errors**
```bash
# Fix volume permissions
docker-compose down -v
docker volume prune
docker-compose up
```

---

## 📚 Best Practices Summary

### ✅ Do's
- Use multi-stage builds to reduce image size
- Run containers as non-root users
- Implement health checks for all services
- Use named volumes for persistent data
- Set resource limits to prevent resource exhaustion
- Use .env files for configuration
- Scan images for vulnerabilities regularly
- Use specific image tags (not `latest`)
- Implement proper logging

### ❌ Don'ts  
- Don't run containers as root
- Don't expose database ports to host in production
- Don't commit .env files to git
- Don't use default passwords
- Don't include secrets in Dockerfiles
- Don't use `latest` tag in production
- Don't skip health checks
- Don't ignore security updates

---

## 🎓 Learning Resources

- [Docker Official Docs](https://docs.docker.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Redis Docker Hub](https://hub.docker.com/_/redis)
- [Nginx Docker Hub](https://hub.docker.com/_/nginx)

---

**🎉 Your application is now fully containerized and production-ready!**
