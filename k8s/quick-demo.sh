#!/bin/bash

# =============================================================================
# Quick Kubernetes Deployment for Portfolio Demo
# =============================================================================

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Quick Kubernetes Setup for Portfolio Demo${NC}\n"

# Check if Minikube is already running
if minikube status &>/dev/null; then
    echo -e "${GREEN}✓ Minikube already running${NC}"
else
    echo -e "${CYAN}➜ Starting Minikube...${NC}"
    minikube start --driver=docker --cpus=4 --memory=4096
    echo -e "${GREEN}✓ Minikube started${NC}"
fi

# Enable metrics
echo -e "${CYAN}➜ Enabling metrics-server...${NC}"
minikube addons enable metrics-server

# Configure Docker
echo -e "${CYAN}➜ Configuring Docker for Minikube...${NC}"
eval $(minikube docker-env)

# Navigate to project
cd "/mnt/c/New Volume (D)/repo/DevOps with AI Antigravity"

# Build images
echo -e "${CYAN}➜ Building backend image...${NC}"
docker build -t ecommerce-backend:v1 ./backend -q
echo -e "${GREEN}✓ Backend built${NC}"

echo -e "${CYAN}➜ Building frontend image...${NC}"
docker build -t ecommerce-frontend:v1 ./frontend -q
echo -e "${GREEN}✓ Frontend built${NC}"

# Create local manifests
cd k8s
echo -e "${CYAN}➜ Preparing manifests...${NC}"
sed 's|image: your-registry/ecommerce-backend:v1|image: ecommerce-backend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g' \
    04-backend-deployment.yaml > 04-backend-deployment-local.yaml
sed 's|image: your-registry/ecommerce-frontend:v1|image: ecommerce-frontend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g; s|type: LoadBalancer|type: NodePort|g' \
    05-frontend-deployment.yaml > 05-frontend-deployment-local.yaml

# Deploy
echo -e "${CYAN}➜ Deploying to Kubernetes...${NC}"
kubectl apply -f 01-namespace-config-secrets.yaml
kubectl apply -f 02-postgres-statefulset.yaml
kubectl apply -f 03-redis-deployment.yaml
kubectl apply -f 04-backend-deployment-local.yaml
kubectl apply -f 05-frontend-deployment-local.yaml

# Wait for deployment
echo -e "${CYAN}➜ Waiting for pods to be ready (this may take 2-3 minutes)...${NC}"
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=120s
kubectl wait --for=condition=ready pod -l app=backend -n ecommerce --timeout=180s
kubectl wait --for=condition=ready pod -l app=frontend -n ecommerce --timeout=120s

# Show status
echo -e "\n${GREEN}✅ Deployment Complete!${NC}\n"
kubectl get all -n ecommerce

# Access info
echo -e "\n${YELLOW}🌐 Access your application:${NC}"
echo -e "   ${CYAN}minikube service frontend -n ecommerce${NC}"
echo -e "\n${YELLOW}📊 Open Kubernetes Dashboard:${NC}"
echo -e "   ${CYAN}minikube dashboard${NC}"
echo -e "\n${YELLOW}📝 Demo commands:${NC}"
echo -e "   ${CYAN}kubectl get pods -n ecommerce${NC}"
echo -e "   ${CYAN}kubectl scale deployment backend --replicas=5 -n ecommerce${NC}"
echo -e "   ${CYAN}kubectl top pods -n ecommerce${NC}"
echo -e "\n${GREEN}🎉 Ready for your demo!${NC}\n"
