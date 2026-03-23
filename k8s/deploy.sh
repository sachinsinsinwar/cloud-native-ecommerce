#!/bin/bash

# ============================================================================= 
# Kubernetes Deployment Script for E-Commerce Application
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="ecommerce"
REGISTRY="your-registry"  # Update this!
VERSION="v1"

# Functions
print_header() {
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}================================${NC}"
}

print_info() {
    echo -e "${YELLOW}➜${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found. Please install kubectl."
        exit 1
    fi
    print_success "kubectl found"
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    print_success "Connected to Kubernetes cluster"
    
    # Check Docker (for building images)
    if ! command -v docker &> /dev/null; then
        print_error "docker not found. Please install Docker."
        exit 1
    fi
    print_success "docker found"
}

update_secrets() {
    print_header "Security Configuration"
    print_info "Generating strong passwords..."
    
    # Generate passwords
    POSTGRES_PASS=$(openssl rand -base64 32)
    REDIS_PASS=$(openssl rand -base64 32)
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Base64 encode
    POSTGRES_PASS_B64=$(echo -n "$POSTGRES_PASS" | base64)
    REDIS_PASS_B64=$(echo -n "$REDIS_PASS" | base64)
    SECRET_KEY_B64=$(echo -n "$SECRET_KEY" | base64)
    
    print_success "Generated secure passwords"
    print_info "Update these in 01-namespace-config-secrets.yaml:"
    echo "  POSTGRES_PASSWORD: $POSTGRES_PASS_B64"
    echo "  REDIS_PASSWORD: $REDIS_PASS_B64"
    echo "  SECRET_KEY: $SECRET_KEY_B64"
    
    read -p "Press Enter after updating the secrets file..."
}

build_and_push_images() {
    print_header "Building and Pushing Container Images"
    
    read -p "Enter your container registry (e.g., gcr.io/project-id): " REGISTRY
    
    # Build backend
    print_info "Building backend image..."
    docker build -t ${REGISTRY}/ecommerce-backend:${VERSION} ../backend
    
    print_info "Pushing backend image..."
    docker push ${REGISTRY}/ecommerce-backend:${VERSION}
    print_success "Backend image pushed"
    
    # Build frontend
    print_info "Building frontend image..."
    docker build -t ${REGISTRY}/ecommerce-frontend:${VERSION} ../frontend
    
    print_info "Pushing frontend image..."
    docker push ${REGISTRY}/ecommerce-frontend:${VERSION}
    print_success "Frontend image pushed"
    
    # Update deployment files
    print_info "Updating deployment files with image references..."
    sed -i "s|your-registry/ecommerce-backend:v1|${REGISTRY}/ecommerce-backend:${VERSION}|g" 04-backend-deployment.yaml
    sed -i "s|your-registry/ecommerce-frontend:v1|${REGISTRY}/ecommerce-frontend:${VERSION}|g" 05-frontend-deployment.yaml
    print_success "Deployment files updated"
}

deploy_application() {
    print_header "Deploying Application to Kubernetes"
    
    # Apply manifests in order
    print_info "Creating namespace, ConfigMaps, and Secrets..."
    kubectl apply -f 01-namespace-config-secrets.yaml
    sleep 2
    
    print_info "Deploying PostgreSQL StatefulSet..."
    kubectl apply -f 02-postgres-statefulset.yaml
    sleep 3
    
    print_info "Deploying Redis..."
    kubectl apply -f 03-redis-deployment.yaml
    sleep 2
    
    print_info "Deploying Backend..."
    kubectl apply -f 04-backend-deployment.yaml
    sleep 2
    
    print_info "Deploying Frontend..."
    kubectl apply -f 05-frontend-deployment.yaml
    
    print_success "All manifests applied"
}

wait_for_pods() {
    print_header "Waiting for Pods to be Ready"
    
    print_info "Waiting for PostgreSQL..."
    kubectl wait --for=condition=ready pod -l app=postgres -n ${NAMESPACE} --timeout=300s
    print_success "PostgreSQL ready"
    
    print_info "Waiting for Redis..."
    kubectl wait --for=condition=ready pod -l app=redis -n ${NAMESPACE} --timeout=120s
    print_success "Redis ready"
    
    print_info "Waiting for Backend..."
    kubectl wait --for=condition=ready pod -l app=backend -n ${NAMESPACE} --timeout=180s
    print_success "Backend ready"
    
    print_info "Waiting for Frontend..."
    kubectl wait --for=condition=ready pod -l app=frontend -n ${NAMESPACE} --timeout=120s
    print_success "Frontend ready"
}

show_status() {
    print_header "Deployment Status"
    
    # Show all resources
    kubectl get all -n ${NAMESPACE}
    
    echo ""
    print_header "Access Information"
    
    # Get service information
    FRONTEND_IP=$(kubectl get svc frontend -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    FRONTEND_PORT=$(kubectl get svc frontend -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].port}')
    
    if [ -n "$FRONTEND_IP" ]; then
        echo "Frontend URL: http://${FRONTEND_IP}:${FRONTEND_PORT}"
    else
        echo "Frontend service type: $(kubectl get svc frontend -n ${NAMESPACE} -o jsonpath='{.spec.type}')"
        echo "Use port-forward for local access:"
        echo "  kubectl port-forward svc/frontend 3000:80 -n ${NAMESPACE}"
    fi
    
    echo ""
    print_info "Useful commands:"
    echo "  View logs: kubectl logs -f -l app=backend -n ${NAMESPACE}"
    echo "  Get pods: kubectl get pods -n ${NAMESPACE}"
    echo "  Describe pod: kubectl describe pod <pod-name> -n ${NAMESPACE}"
    echo "  Access PostgreSQL: kubectl exec -it postgres-0 -n ${NAMESPACE} -- psql -U postgres -d ecommerce_db"
}

# Main execution
main() {
    print_header "E-Commerce Kubernetes Deployment"
    
    echo "This script will:"
    echo "  1. Check prerequisites"
    echo "  2. Generate secure passwords"
    echo "  3. Build and push container images"
    echo "  4. Deploy to Kubernetes"
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    
    check_prerequisites
    update_secrets
    
    read -p "Build and push images? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_and_push_images
    fi
    
    deploy_application
    wait_for_pods
    show_status
    
    print_success "Deployment complete!"
}

# Run main function
main
