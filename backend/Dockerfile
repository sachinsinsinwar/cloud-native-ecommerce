# =============================================================================
# Flask Backend Dockerfile
# Base Image: Python 3.9-slim
# Purpose: Containerize the Flask API with optimized build and security
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder Stage
# Purpose: Install dependencies and prepare the application
# Why multi-stage? Reduces final image size by excluding build tools
# -----------------------------------------------------------------------------
FROM python:3.9-slim AS builder

# Base Image Reasoning:
# - python:3.9-slim: Smaller than full python:3.9 (~150MB vs ~900MB)
# - Includes essential packages while removing unnecessary documentation
# - Security: Debian-based, receives regular security updates
# - Stability: Python 3.9 has long-term support until 2025

# Set working directory
WORKDIR /app

# Security Best Practice: Run as non-root user
# Create a dedicated user for running the application
RUN groupadd -r flaskuser && useradd -r -g flaskuser flaskuser

# Install system dependencies required for Python packages
# postgresql-client: For database connectivity
# gcc: Required for compiling some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Security: Clean up apt cache to reduce image size and attack surface

# Copy requirements first for better layer caching
# This layer is cached unless requirements.txt changes
COPY requirements.txt .

# Install Python dependencies
# --no-cache-dir: Don't cache pip packages (saves space)
# --upgrade: Ensure latest compatible versions
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime Stage
# Purpose: Create minimal production image
# -----------------------------------------------------------------------------
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Security: Create non-root user (same as builder)
RUN groupadd -r flaskuser && useradd -r -g flaskuser flaskuser

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
RUN apt-get update && apt-get install -y --only-upgrade openssl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=flaskuser:flaskuser . .

# Security: Change ownership to non-root user
RUN chown -R flaskuser:flaskuser /app

# Switch to non-root user
USER flaskuser

# Environment Variables (override in docker-compose or runtime)
# PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Expose port 5000 (Flask default)
# Note: This is documentation only, actual port binding happens at runtime
EXPOSE 5000

# Health check
# Ensures container is healthy and ready to receive traffic
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Default command
# Use gunicorn for production (better than Flask dev server)
# -w 4: 4 worker processes (adjust based on CPU cores)
# -b 0.0.0.0:5000: Bind to all interfaces
# --timeout 120: Request timeout in seconds
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]

# Alternative command for development (uncomment if needed):
# CMD ["python", "app.py"]

# =============================================================================
# Required Environment Variables (set in docker-compose.yml or .env):
# =============================================================================
# DATABASE_URL=postgresql://user:password@postgres:5432/dbname
# REDIS_URL=redis://redis:6379/0
# SECRET_KEY=your-secret-key-here-use-strong-random-value
# FLASK_ENV=production|development
# CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
# =============================================================================
