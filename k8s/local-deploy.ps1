# =============================================================================
# Minikube Local Testing - Quick Start Script
# =============================================================================
# This script automates the setup of your e-commerce app on Minikube
# =============================================================================

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor $Green
    Write-Host $Message -ForegroundColor $Green
    Write-Host "========================================`n" -ForegroundColor $Green
}

function Write-Step {
    param([string]$Message)
    Write-Host "➜ $Message" -ForegroundColor $Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor $Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor $Red
}

# =============================================================================
# STEP 1: Check Prerequisites
# =============================================================================

Write-Header "Checking Prerequisites"

# Check if Minikube is installed
Write-Step "Checking for Minikube..."
if (Get-Command minikube -ErrorAction SilentlyContinue) {
    Write-Success "Minikube found: $(minikube version --short)"
} else {
    Write-Error-Custom "Minikube not found!"
    Write-Warning "Install with: choco install minikube -y"
    exit 1
}

# Check if kubectl is installed
Write-Step "Checking for kubectl..."
if (Get-Command kubectl -ErrorAction SilentlyContinue) {
    Write-Success "kubectl found: $(kubectl version --client --short)"
} else {
    Write-Error-Custom "kubectl not found!"
    Write-Warning "Install with: choco install kubernetes-cli -y"
    exit 1
}

# Check if Docker is installed
Write-Step "Checking for Docker..."
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Success "Docker found: $(docker --version)"
} else {
    Write-Error-Custom "Docker not found!"
    Write-Warning "Install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
}

# =============================================================================
# STEP 2: Start Minikube
# =============================================================================

Write-Header "Starting Minikube"

# Check if Minikube is already running
$minikubeStatus = minikube status 2>$null
if ($LASTEXITCODE -eq 0 -and $minikubeStatus -match "Running") {
    Write-Success "Minikube is already running"
} else {
    Write-Step "Starting Minikube cluster (this may take a few minutes)..."
    minikube start --driver=docker --cpus=4 --memory=4096
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Minikube started successfully"
    } else {
        Write-Error-Custom "Failed to start Minikube"
        exit 1
    }
}

# Enable required addons
Write-Step "Enabling metrics-server addon..."
minikube addons enable metrics-server
Write-Success "metrics-server enabled"

# =============================================================================
# STEP 3: Configure Docker Environment
# =============================================================================

Write-Header "Configuring Docker for Minikube"

Write-Step "Setting Docker environment to use Minikube's Docker daemon..."
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

if ($LASTEXITCODE -eq 0) {
    Write-Success "Docker environment configured"
    Write-Warning "Images will be built in Minikube's Docker daemon"
} else {
    Write-Error-Custom "Failed to configure Docker environment"
    exit 1
}

# =============================================================================
# STEP 4: Build Container Images
# =============================================================================

Write-Header "Building Container Images"

# Navigate to project root
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

Write-Step "Building backend image..."
docker build -t ecommerce-backend:v1 ./backend
if ($LASTEXITCODE -eq 0) {
    Write-Success "Backend image built"
} else {
    Write-Error-Custom "Failed to build backend image"
    exit 1
}

Write-Step "Building frontend image..."
docker build -t ecommerce-frontend:v1 ./frontend
if ($LASTEXITCODE -eq 0) {
    Write-Success "Frontend image built"
} else {
    Write-Error-Custom "Failed to build frontend image"
    exit 1
}

# Verify images
Write-Step "Verifying images..."
docker images | Select-String "ecommerce"

# =============================================================================
# STEP 5: Create Local Deployment Manifests
# =============================================================================

Write-Header "Preparing Deployment Manifests"

Set-Location "$projectRoot\k8s"

# Create local backend deployment
Write-Step "Creating local backend deployment manifest..."
(Get-Content 04-backend-deployment.yaml) | ForEach-Object {
    $_ -replace 'image: your-registry/ecommerce-backend:v1', 'image: ecommerce-backend:v1' `
       -replace 'imagePullPolicy: Always', 'imagePullPolicy: Never'
} | Set-Content 04-backend-deployment-local.yaml
Write-Success "Local backend manifest created"

# Create local frontend deployment
Write-Step "Creating local frontend deployment manifest..."
(Get-Content 05-frontend-deployment.yaml) | ForEach-Object {
    $_ -replace 'image: your-registry/ecommerce-frontend:v1', 'image: ecommerce-frontend:v1' `
       -replace 'imagePullPolicy: Always', 'imagePullPolicy: Never' `
       -replace 'type: LoadBalancer', 'type: NodePort'
} | Set-Content 05-frontend-deployment-local.yaml
Write-Success "Local frontend manifest created"

# =============================================================================
# STEP 6: Deploy to Kubernetes
# =============================================================================

Write-Header "Deploying Application to Kubernetes"

# Deploy namespace, configmaps, secrets
Write-Step "Creating namespace, ConfigMaps, and Secrets..."
kubectl apply -f 01-namespace-config-secrets.yaml
Start-Sleep -Seconds 2
Write-Success "Namespace and configs created"

# Deploy PostgreSQL
Write-Step "Deploying PostgreSQL StatefulSet..."
kubectl apply -f 02-postgres-statefulset.yaml
Write-Success "PostgreSQL deployment submitted"

Write-Step "Waiting for PostgreSQL to be ready (this may take a minute)..."
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce --timeout=300s
Write-Success "PostgreSQL is ready"

# Deploy Redis
Write-Step "Deploying Redis..."
kubectl apply -f 03-redis-deployment.yaml
Write-Success "Redis deployment submitted"

Write-Step "Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=120s
Write-Success "Redis is ready"

# Deploy Backend
Write-Step "Deploying Backend..."
kubectl apply -f 04-backend-deployment-local.yaml
Write-Success "Backend deployment submitted"

Write-Step "Waiting for Backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n ecommerce --timeout=180s
Write-Success "Backend is ready"

# Deploy Frontend
Write-Step "Deploying Frontend..."
kubectl apply -f 05-frontend-deployment-local.yaml
Write-Success "Frontend deployment submitted"

Write-Step "Waiting for Frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n ecommerce --timeout=120s
Write-Success "Frontend is ready"

# =============================================================================
# STEP 7: Verify Deployment
# =============================================================================

Write-Header "Deployment Verification"

Write-Step "Getting all resources in ecommerce namespace..."
kubectl get all -n ecommerce

Write-Step "`nChecking pod status..."
kubectl get pods -n ecommerce

# =============================================================================
# STEP 8: Access Information
# =============================================================================

Write-Header "Access Information"

Write-Host "✓ All services are deployed and running!" -ForegroundColor $Green
Write-Host ""
Write-Host "Access your application using the following methods:" -ForegroundColor $Cyan
Write-Host ""
Write-Host "1. Minikube Service (Recommended - opens browser):" -ForegroundColor $Yellow
Write-Host "   minikube service frontend -n ecommerce" -ForegroundColor $Green
Write-Host ""
Write-Host "2. Port Forwarding:" -ForegroundColor $Yellow
Write-Host "   kubectl port-forward svc/frontend 3000:80 -n ecommerce" -ForegroundColor $Green
Write-Host "   Then open: http://localhost:3000" -ForegroundColor $Cyan
Write-Host ""
Write-Host "3. Get NodePort:" -ForegroundColor $Yellow
Write-Host "   `$nodePort = kubectl get svc frontend -n ecommerce -o jsonpath='{.spec.ports[0].nodePort}'" -ForegroundColor $Green
Write-Host "   `$minikubeIP = minikube ip" -ForegroundColor $Green
Write-Host "   Then open: http://`$minikubeIP:`$nodePort" -ForegroundColor $Cyan
Write-Host ""

Write-Host "Useful commands:" -ForegroundColor $Yellow
Write-Host "  View backend logs:    kubectl logs -f -l app=backend -n ecommerce" -ForegroundColor $Green
Write-Host "  View frontend logs:   kubectl logs -f -l app=frontend -n ecommerce" -ForegroundColor $Green
Write-Host "  Access PostgreSQL:    kubectl exec -it postgres-0 -n ecommerce -- psql -U postgres -d ecommerce_db" -ForegroundColor $Green
Write-Host "  View all pods:        kubectl get pods -n ecommerce" -ForegroundColor $Green
Write-Host "  Open dashboard:       minikube dashboard" -ForegroundColor $Green
Write-Host ""

# =============================================================================
# STEP 9: Offer to Open Browser
# =============================================================================

$openBrowser = Read-Host "Would you like to open the frontend in your browser now? (Y/n)"
if ($openBrowser -ne 'n' -and $openBrowser -ne 'N') {
    Write-Step "Opening frontend in browser..."
    minikube service frontend -n ecommerce
}

Write-Host ""
Write-Success "Deployment complete! Happy testing! 🚀"
Write-Host ""
Write-Warning "To cleanup: kubectl delete namespace ecommerce"
Write-Warning "To stop Minikube: minikube stop"
Write-Host ""
