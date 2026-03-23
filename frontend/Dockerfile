# =============================================================================
# React Frontend Dockerfile
# Base Image: Node 16-alpine
# Purpose: Containerize React app with optimized multi-stage build
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Development Stage (for local development with hot-reload)
# -----------------------------------------------------------------------------
FROM node:20-alpine AS development

# Base Image Reasoning:
# - node:20-alpine: Minimal Alpine Linux base (~40MB vs ~900MB for full Node)
# - Node 20 LTS: Current Long-term support, stable, latest features
# - Alpine: Lightweight, security-focused, minimal attack surface
# - apk package manager: Fast and efficient

# Set working directory
WORKDIR /app

# Security Best Practice: Run as non-root user
# Alpine uses 'node' user by default, but we'll be explicit
RUN addgroup -g 1001 -S nodejs && \
    adduser -S reactuser -u 1001 -G nodejs

# Copy package files first (for layer caching)
# This layer is cached unless package.json or package-lock.json changes
COPY package*.json ./

# Install dependencies
# --frozen-lockfile: Ensures consistent installs using package-lock.json
RUN npm ci --frozen-lockfile

# Copy application source code
COPY --chown=reactuser:nodejs . .

# Switch to non-root user
USER reactuser

# Expose Vite development server port
EXPOSE 3000

# Development command with hot-reload
# --host: Allow external connections (needed for Docker)
CMD ["npm", "run", "dev", "--", "--host"]

# -----------------------------------------------------------------------------
# Stage 2: Builder Stage  (for production build)
# -----------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies for build)
RUN npm ci --frozen-lockfile

# Copy source code
COPY . .

# Build Arguments (can be passed during docker build)
# Example: docker build --build-arg VITE_API_URL=https://api.example.com
ARG VITE_API_URL=http://localhost:5000
ENV VITE_API_URL=$VITE_API_URL

# Build the React application
# Creates optimized production bundle in /app/dist
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 3: Production Stage (nginx to serve static files)
# Purpose: Lightweight production server for static React app
# -----------------------------------------------------------------------------
FROM nginx:1.25-alpine AS production

# Base Image Reasoning:
# - nginx:alpine: Industry-standard web server, highly efficient
# - Alpine variant: Minimal size (~25MB), perfect for static files
# - nginx: Fast, battle-tested, excellent for serving SPAs

# Security: Run nginx as non-root
# Create nginx user and group if not exists
RUN addgroup -g 101 -S nginx 2>/dev/null || true && \
    adduser -S nginx -u 101 -G nginx 2>/dev/null || true

# Copy custom nginx configuration
# This config handles React Router (SPA routing)
COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;

    # SPA routing - redirect all requests to index.html
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Cache static assets
    location ~* \\.(?:css|js|jpg|jpeg|gif|png|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Security: Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    chown -R nginx:nginx /etc/nginx/conf.d

# Create nginx PID directory with proper permissions
RUN touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Switch to non-root user
USER nginx

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

# Start nginx in foreground
CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# Required Build Arguments:
# =============================================================================
# VITE_API_URL: Backend API URL (default: http://localhost:5000)
#
# Build Examples:
# - Development: docker build --target development -t frontend:dev .
# - Production:  docker build --target production -t frontend:prod \
#                --build-arg VITE_API_URL=https://api.example.com .
# =============================================================================
