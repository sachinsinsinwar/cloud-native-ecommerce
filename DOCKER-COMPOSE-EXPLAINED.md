# Docker Compose Explained - Section by Section

## 📚 Complete Guide to Your docker-compose.yml

This guide breaks down every part of your Docker Compose configuration with clear explanations.

---

## 🎯 Overview

Your `docker-compose.yml` orchestrates **4 services**:

```
┌─────────────────────────────────────────────┐
│         ecommerce-network                   │
│         (172.25.0.0/16)                     │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Frontend  │─▶│ Backend  │─▶│PostgreSQL│ │
│  │(React)   │  │ (Flask)  │  │ (DB)     │ │
│  │Port:3000 │  │Port:5000 │  │Port:5432 │ │
│  └──────────┘  └─────┬────┘  └──────────┘ │
│                      │                      │
│                      ▼                      │
│                 ┌──────────┐                │
│                 │  Redis   │                │
│                 │ (Cache)  │                │
│                 │Port:6379 │                │
│                 └──────────┘                │
└─────────────────────────────────────────────┘
```

---

## 📋 Section 1: Version

```yaml
version: '3.8'
```

**What it means:**
- Specifies Docker Compose file format version
- Version 3.8 supports all modern features
- Higher versions require newer Docker Engine

**Why 3.8?**
- ✅ Widely compatible
- ✅ Supports health checks, resource limits, build args
- ✅ Works with Docker Engine 19.03.0+

---

## 📋 Section 2: Services

### Service 1: PostgreSQL Database

```yaml
services:
  postgres:
    image: postgres:14-alpine
    container_name: ecommerce-postgres
    restart: unless-stopped
```

#### **Image Selection**
```yaml
image: postgres:14-alpine
```
- **postgres:14** = PostgreSQL version 14 (LTS)
- **alpine** = Lightweight Linux distribution
- **Size**: ~200MB (vs ~350MB for debian variant)

#### **Container Name**
```yaml
container_name: ecommerce-postgres
```
- Friendly name for logs and commands
- Use: `docker logs ecommerce-postgres`

#### **Restart Policy**
```yaml
restart: unless-stopped
```
**Options:**
- `no` - Never restart
- `always` - Always restart (even after reboot)
- `on-failure` - Only restart on error
- `unless-stopped` - Restart unless manually stopped ✅ RECOMMENDED

#### **Environment Variables**
```yaml
environment:
  POSTGRES_USER: ${POSTGRES_USER:-postgres}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
  POSTGRES_DB: ${POSTGRES_DB:-ecommerce_db}
```

**Syntax explained:**
- `${VARIABLE:-default}` = Use .env value OR default
- Example: If `.env` has `POSTGRES_USER=admin`, uses `admin`
- If not in `.env`, uses default `postgres`

**Security:**
```yaml
POSTGRES_HOST_AUTH_METHOD: md5  # Require password
```

#### **Port Mapping**
```yaml
ports:
  - "${POSTGRES_PORT:-5432}:5432"
```

**Format:** `"host_port:container_port"`
- **5432:5432** = Port 5432 on your computer → Port 5432 in container
- Access from host: `localhost:5432`
- Access from other containers: `postgres:5432`

⚠️ **Production Tip:** Remove `ports:` section (don't expose database externally)

#### **Volumes (Data Persistence)**
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data  # Data storage
  - ./database/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro # Schema
  - ./database/seed.sql:/docker-entrypoint-initdb.d/02-seed.sql:ro # Data
```

**Volume Types:**

1. **Named Volume** (managed by Docker)
   ```yaml
   postgres_data:/var/lib/postgresql/data
   ```
   - Data survives container removal
   - Located in Docker's storage area
   - Managed with `docker volume` commands

2. **Bind Mount** (your file → container)
   ```yaml
   ./database/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
   ```
   - `:ro` = read-only
   - Files in `/docker-entrypoint-initdb.d/` run on first startup
   - Numbered (01-, 02-) to control order

#### **Health Check**
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d ecommerce_db"]
  interval: 10s    # Check every 10 seconds
  timeout: 5s      # Wait up to 5 seconds
  retries: 5       # Try 5 times before unhealthy
  start_period: 10s # Grace period during startup
```

**What it does:**
- Docker monitors container health
- Other services wait for "healthy" status
- Auto-restarts if check fails repeatedly

#### **Resource Limits**
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'     # Maximum 1 CPU core
      memory: 512M    # Maximum 512 MB RAM
    reservations:
      cpus: '0.5'     # Guaranteed 0.5 CPU
      memory: 256M    # Guaranteed 256 MB
```

**Why set limits?**
- Prevents one container from consuming all resources
- Ensures fair resource distribution
- Protects other services from resource starvation

---

### Service 2: Redis Cache

```yaml
redis:
  image: redis:7-alpine
  command: >
    redis-server
    --appendonly yes
    --appendfsync everysec
    --maxmemory 256mb
    --maxmemory-policy allkeys-lru
```

#### **Redis Configuration**
**Flag Explanations:**

1. `--appendonly yes`
   - Enables AOF (Append Only File) persistence
   - Writes every command to disk
   - Data survives restarts

2. `--appendfsync everysec`
   - Syncs to disk every second
   - **Balance:** Performance vs durability
   - **Alternatives:** `always` (slower, safer) or `no` (faster, risky)

3. `--maxmemory 256mb`
   - Limits RAM usage to 256 MB
   - Prevents Redis from consuming all memory

4. `--maxmemory-policy allkeys-lru`
   - **LRU** = Least Recently Used
   - When memory full, removes oldest unused keys
   - **Alternatives:** `allkeys-lfu`, `volatile-lru`, `noeviction`

---

### Service 3: Flask Backend

```yaml
backend:
  build:
    context: ./backend
    dockerfile: Dockerfile
```

#### **Build vs Image**
```yaml
# Option 1: Build from Dockerfile (what we use)
build:
  context: ./backend

# Option 2: Pull pre-built image
# image: myregistry/backend:latest
```

**Why build locally?**
- You have the source code
- Can modify and rebuild easily
- No need for image registry (DockerHub, etc.)

#### **Environment Variables**
```yaml
environment:
  DATABASE_URL: postgresql://user:pass@postgres:5432/db
  REDIS_URL: redis://:@redis:6379/0
```

**Connection String Format:**

**PostgreSQL:**
```
postgresql://username:password@hostname:port/database_name
```
- `@postgres` = service name from docker-compose (not `localhost`!)
- Docker DNS resolves `postgres` to container IP

**Redis:**
```
redis://:password@hostname:port/database_number
```
- `:password@` = `:` before password (leave empty if no password)
- `/0` = Redis database number (0-15 available)

#### **Depends On with Condition**
```yaml
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

**What happens:**
1. Docker starts PostgreSQL
2. Docker waits for PostgreSQL health check to pass
3. Docker starts Redis
4. Docker waits for Redis health check to pass
5. **Only then** Docker starts backend

**Why important?**
- Backend needs database to be ready
- Prevents connection errors during startup
- Services start in correct order

---

### Service 4: React Frontend

```yaml
frontend:
  build:
    target: ${FRONTEND_BUILD_TARGET:-production}
    args:
      VITE_API_URL: ${VITE_API_URL:-http://localhost:5000}
```

#### **Multi-Stage Build Target**
```yaml
target: ${FRONTEND_BUILD_TARGET:-production}
```

Your Dockerfile has multiple stages:
- `development` - Vite dev server (hot-reload)
- `builder` - Builds React app
- `production` - Nginx serves built files

**Set in .env:**
```bash
# For development
FRONTEND_BUILD_TARGET=development
FRONTEND_INTERNAL_PORT=3000

# For production
FRONTEND_BUILD_TARGET=production
FRONTEND_INTERNAL_PORT=80
```

#### **Build Arguments**
```yaml
args:
  VITE_API_URL: ${VITE_API_URL:-http://localhost:5000}
```

**Build Args vs Environment Variables:**

| Build Args | Environment Variables |
|------------|----------------------|
| Set at **build** time | Set at **runtime** |
| Baked into image | Can change per container |
| For React/Vite | For backend config |
| Example: API URLs | Example: DB credentials |

---

## 📋 Section 3: Networks

```yaml
networks:
  ecommerce-network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.25.0.0/16
```

### **How Container Networking Works**

**Without Custom Network:**
- Containers use default bridge
- Can only communicate by IP (192.168.x.x)
- No DNS resolution

**With Custom Network:**
- Automatic DNS: Use service names as hostnames
- Isolated from other Docker networks
- Backend connects to `postgres:5432` (not `localhost:5432`)

**Example:**
```python
# In Flask app:
DATABASE_URL = "postgresql://user:pass@postgres:5432/db"
#                                      ^^^^^^^^
#                            Service name, NOT localhost!
```

**IPAM (IP Address Management):**
- Assigns custom subnet `172.25.0.0/16`
- Predictable IP addresses
- Easier debugging and firewall rules

---

## 📋 Section 4: Volumes

```yaml
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
```

### **Named Volumes Explained**

**What Docker does:**
1. Creates directory in Docker's storage
   - Linux: `/var/lib/docker/volumes/`
   - Windows: `C:\ProgramData\Docker\volumes\`
   - Mac: `/var/lib/docker/volumes/`

2. Mounts this directory into container
   - `postgres_data` → `/var/lib/postgresql/data`

3. Data persists even when container deleted

**Volume Commands:**
```bash
# List volumes
docker volume ls

# Inspect volume location
docker volume inspect devopswithaiantigravity_postgres_data

# Backup volume
docker run --rm -v postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/db_backup.tar.gz /data

# Remove volume (⚠️ deletes data)
docker volume rm devopswithaiantigravity_postgres_data
```

---

## 🚀 Usage Examples

### Start All Services
```bash
docker-compose up --build
```
**Flags:**
- `--build` - Rebuild images before starting
- `-d` - Detached mode (run in background)
- `--force-recreate` - Recreate containers even if no changes

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 frontend
```

### Execute Commands
```bash
# Shell into backend
docker-compose exec backend /bin/sh

# Run Django migrations
docker-compose exec backend python manage.py migrate

# PostgreSQL CLI
docker-compose exec postgres psql -U postgres -d ecommerce_db

# Redis CLI
docker-compose exec redis redis-cli
```

### Stop Services
```bash
# Stop (keep containers)
docker-compose stop

# Stop and remove (keep volumes)
docker-compose down

# Stop, remove, and delete volumes
docker-compose down -v
```

### Check Status
```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Health status
docker inspect --format='{{.State.Health.Status}}' ecommerce-backend
```

---

## 🔧 Configuration Flow

```
.env file
   ↓
docker-compose.yml
   ↓
Services start in order:
   1. postgres (waits for health check)
   2. redis (waits for health check)
   3. backend (waits for postgres + redis)
   4. frontend (waits for backend)
   ↓
All services running!
```

---

## 📚 Key Takeaways

1. **Service Names = Hostnames**
   - `postgres` not `localhost` in connection strings

2. **Health Checks Enable Safe Startup**
   - `depends_on` with `condition: service_healthy`

3. **Named Volumes Persist Data**
   - Survives `docker-compose down`
   - Lost with `docker-compose down -v`

4. **Environment Variables**
   - .env file → docker-compose.yml → containers

5. **Resource Limits Protect Your System**
   - Prevents one container from hogging resources

6. **Networks Enable Communication**
   - Custom network with DNS resolution

---

## 🎓 Next Steps

1. ✅ Review this guide
2. ⚙️ Edit `.env` file (copy from `.env.docker`)
3. 🚀 Run `docker-compose up --build`
4. 🧪 Test: `http://localhost:3000`
5. 📊 Monitor: `docker-compose logs -f`

Your Docker orchestration is complete and production-ready! 🎉
