#!/bin/bash

# =============================================================================
# E-Commerce Minikube Deployment Script for Ubuntu WSL
# =============================================================================

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_PATH="/mnt/c/New Volume (D)/repo/DevOps with AI Antigravity"

# Functions
print_header() {
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}======================================${NC}"
}

print_step() {
    echo -e "${CYAN}➜${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_command() {
    if command -v $1 &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# =============================================================================
# STEP 1: Check Prerequisites
# =============================================================================

print_header "Checking Prerequisites"

# Check Docker
if ! check_command docker; then
    echo ""
    print_warning "Install Docker with:"
    echo "  sudo apt update"
    echo "  sudo apt install -y docker.io"
    echo "  sudo usermod -aG docker \$USER"
    echo "  newgrp docker"
    exit 1
fi

# Check if Docker is running
if ! sudo service docker status > /dev/null 2>&1; then
    print_step "Starting Docker service..."
    sudo service docker start
    sleep 2
fi

# Test Docker
if docker ps > /dev/null 2>&1; then
    print_success "Docker is running"
else
    print_error "Docker is not running properly"
    print_warning "Try: sudo service docker start"
    exit 1
fi

# Check kubectl
if ! check_command kubectl; then
    echo ""
    print_warning "Install kubectl with:"
    echo '  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"'
    echo "  chmod +x kubectl"
    echo "  sudo mv kubectl /usr/local/bin/"
    exit 1
fi

# Check Minikube
if ! check_command minikube; then
    echo ""
    print_warning "Install Minikube with:"
    echo "  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64"
    echo "  sudo install minikube-linux-amd64 /usr/local/bin/minikube"
    exit 1
fi

# =============================================================================
# STEP 2: Start Minikube
# =============================================================================

print_header "Starting Minikube"

# Check if Minikube is already running
if minikube status | grep -q "Running"; then
    print_success "Minikube is already running"
else
    print_step "Starting Minikube cluster (this may take 3-5 minutes)..."
    minikube start --driver=docker --cpus=4 --memory=4096
    print_success "Minikube started successfully"
fi

# Enable metrics-server
print_step "Enabling metrics-server addon..."
minikube addons enable metrics-server
print_success "Metrics-server enabled"

# =============================================================================
# STEP 3: Configure Docker for Minikube
# =============================================================================

print_header "Configuring Docker Environment"

print_step "Setting Docker to use Minikube's daemon..."
eval $(minikube docker-env)
print_success "Docker configured for Minikube"

# =============================================================================
# STEP 4: Build Container Images
# =============================================================================

print_header "Building Container Images"

# Navigate to project
if [ ! -d "$PROJECT_PATH" ]; then
    print_error "Project directory not found: $PROJECT_PATH"
    print_warning "Update PROJECT_PATH variable in this script"
    exit 1
fi

cd "$PROJECT_PATH"
print_success "Project directory: $PROJECT_PATH"

# Build backend
print_step "Building backend image..."
docker build -t ecommerce-backend:v1 ./backend
print_success "Backend image built"

# Build frontend
print_step "Building frontend image..."
docker build -t ecommerce-frontend:v1 ./frontend
print_success "Frontend image built"

# Verify images
print_step "Verifying images..."
docker images | grep ecommerce

# =============================================================================
# STEP 5: Prepare Local Manifests
# =============================================================================

print_header "Preparing Deployment Manifests"

cd "$PROJECT_PATH/k8s"

# Create local backend manifest
print_step "Creating local backend manifest..."
sed 's|image: your-registry/ecommerce-backend:v1|image: ecommerce-backend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g' \
    04-backend-deployment.yaml > 04-backend-deployment-local.yaml
print_success "Backend manifest created"

# Create local frontend manifest
print_step "Creating local frontend manifest..."
sed 's|image: your-registry/ecommerce-frontend:v1|image: ecommerce-frontend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g; s|type: LoadBalancer|type: NodePort|g' \
    05-frontend-deployment.yaml > 05-frontend-deployment-local.yaml
print_success "Frontend manifest created"

# =============================================================================
# STEP 6: Deploy to Kubernetes
# =============================================================================

print_header "Deploying Application to Kubernetes"

# Deploy namespace and configs
print_step "Creating namespace, ConfigMaps, and Secrets..."
kubectl apply -f 01-namespace-config-secrets.yaml
sleep 2
print_success "Namespace and configs created"

# Deploy PostgreSQL
print_step "Deploying PostgreSQL StatefulSet..."
kubectl apply -f 02-postgres-statefulset.yaml
print_success "PostgreSQL deployment submitted"

print_step "Waiting for PostgreSQL to be ready (this may take 1-2 minutes)..."
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce --timeout=300s
print_success "PostgreSQL is ready"

# Deploy Redis
print_step "Deploying Redis..."
kubectl apply -f 03-redis-deployment.yaml
print_success "Redis deployment submitted"

print_step "Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=120s
print_success "Redis is ready"

# Deploy Backend
print_step "Deploying Backend..."
kubectl apply -f 04-backend-deployment-local.yaml
print_success "Backend deployment submitted"

print_step "Waiting for Backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n ecommerce --timeout=180s
print_success "Backend is ready"

# Deploy Frontend
echo -e "${CYAN}➜ Deploying frontend...${NC}"
kubectl apply -f 05-frontend-deployment-local.yaml
echo -e "${GREEN}✓ Frontend deployed${NC}"

# Deploy Ingress
echo -e "${CYAN}➜ Deploying Ingress (optional)...${NC}"
if kubectl get pods -n ingress-nginx &>/dev/null; then
    kubectl apply -f 09-ingress-local.yaml
    echo -e "${GREEN}✓ Ingress deployed${NC}"
else
    echo -e "${YELLOW}⚠ Ingress controller not found. Enable with: minikube addons enable ingress${NC}"
fi

print_step "Waiting for Frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n ecommerce --timeout=120s
print_success "Frontend is ready"

# =============================================================================
# STEP 7: Verification
# =============================================================================

print_header "Deployment Verification"

print_step "Getting all resources..."
kubectl get all -n ecommerce

echo ""
print_step "Checking pod status..."
kubectl get pods -n ecommerce

# =============================================================================
# STEP 8: Access Information
# =============================================================================

print_header "Access Information"

echo -e "${GREEN}✓ All services are deployed and running!${NC}"
echo ""
echo -e "${CYAN}Access your application using:${NC}"
echo ""
echo -e "${YELLOW}Method 1 - Minikube Service (Recommended):${NC}"
echo -e "${GREEN}  minikube service frontend -n ecommerce${NC}"
echo ""
echo -e "${YELLOW}Method 2 - Port Forwarding:${NC}"
echo -e "${GREEN}  kubectl port-forward svc/frontend 3000:80 -n ecommerce${NC}"
echo -e "${CYAN}  Then open: http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}Method 3 - Direct NodePort:${NC}"
MINIKUBE_IP=$(minikube ip)
NODE_PORT=$(kubectl get svc frontend -n ecommerce -o jsonpath='{.spec.ports[0].nodePort}')
echo -e "${CYAN}  http://${MINIKUBE_IP}:${NODE_PORT}${NC}"
echo ""

echo -e "${YELLOW}Useful commands:${NC}"
echo -e "${GREEN}  View backend logs:     kubectl logs -f -l app=backend -n ecommerce${NC}"
echo -e "${GREEN}  View frontend logs:    kubectl logs -f -l app=frontend -n ecommerce${NC}"
echo -e "${GREEN}  Access PostgreSQL:     kubectl exec -it postgres-0 -n ecommerce -- psql -U postgres -d ecommerce_db${NC}"
echo -e "${GREEN}  View all pods:         kubectl get pods -n ecommerce${NC}"
echo -e "${GREEN}  Open dashboard:        minikube dashboard${NC}"
echo -e "${GREEN}  Cleanup:               kubectl delete namespace ecommerce${NC}"
echo ""

# =============================================================================
# STEP 9: Verify Health
# =============================================================================

print_header "Health Checks"

# Check PostgreSQL
print_step "Checking PostgreSQL..."
if kubectl exec -it postgres-0 -n ecommerce -- psql -U postgres -d ecommerce_db -c "SELECT COUNT(*) FROM products;" > /dev/null 2>&1; then
    print_success "PostgreSQL is healthy and has seed data"
else
    print_warning "PostgreSQL might need a moment to initialize"
fi

# Check Redis
print_step "Checking Redis..."
REDIS_POD=$(kubectl get pod -n ecommerce -l app=redis -o jsonpath='{.items[0].metadata.name}')
if kubectl exec -it $REDIS_POD -n ecommerce -- redis-cli ping | grep -q "PONG"; then
    print_success "Redis is healthy"
else
    print_warning "Redis health check failed"
fi

# Check Backend
print_step "Checking Backend API..."
BACKEND_POD=$(kubectl get pod -n ecommerce -l app=backend -o jsonpath='{.items[0].metadata.name}')
if kubectl exec -it $BACKEND_POD -n ecommerce -- wget -qO- http://localhost:5000/health | grep -q "healthy"; then
    print_success "Backend API is healthy"
else
    print_warning "Backend API health check failed"
fi

# =============================================================================
# COMPLETION
# =============================================================================

echo ""
print_success "Deployment complete! 🚀"
echo ""
print_warning "To cleanup: kubectl delete namespace ecommerce"
print_warning "To stop Minikube: minikube stop"
echo ""
