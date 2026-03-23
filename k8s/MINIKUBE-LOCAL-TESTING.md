# Local Kubernetes Testing with Minikube

This guide walks you through setting up Minikube on Windows and deploying your e-commerce application locally for testing.

---

## 📋 Prerequisites

- **Windows 10/11** with Hyper-V or WSL2
- **At least 4GB RAM** available (8GB recommended)
- **At least 20GB free disk space**
- **Administrator access**

---

## 🚀 Part 1: Installing Minikube on Windows

### Method 1: Using Chocolatey (Recommended)

```powershell
# Install Chocolatey if not already installed
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install kubectl
choco install kubernetes-cli -y

# Install Minikube
choco install minikube -y

# Verify installations
kubectl version --client
minikube version
```

### Method 2: Manual Installation

1. **Download kubectl:**
   ```powershell
   curl.exe -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"
   ```

2. **Download Minikube:**
   ```powershell
   # Download Minikube installer
   Invoke-WebRequest -Uri "https://github.com/kubernetes/minikube/releases/latest/download/minikube-installer.exe" -OutFile "minikube-installer.exe"
   
   # Run installer
   .\minikube-installer.exe
   ```

3. **Add to PATH:**
   - Open System Properties → Environment Variables
   - Add kubectl and minikube directories to PATH
   - Restart terminal

### Install Docker Desktop (Required)

Minikube needs a container runtime. Docker Desktop is the easiest option for Windows.

1. Download from: https://www.docker.com/products/docker-desktop
2. Install and restart computer
3. Verify: `docker --version`

---

## 🎯 Part 2: Starting Minikube

### Start Minikube Cluster

```powershell
# Start Minikube with Docker driver
minikube start --driver=docker --cpus=4 --memory=4096

# Or with Hyper-V (requires Hyper-V enabled)
# minikube start --driver=hyperv --cpus=4 --memory=4096

# Verify cluster is running
minikube status
kubectl cluster-info
```

**Expected output:**
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

### Enable Required Addons

```powershell
# Enable metrics-server (required for HPA)
minikube addons enable metrics-server

# Enable ingress (optional, for testing ingress)
minikube addons enable ingress

# Enable registry (optional, for local image registry)
minikube addons enable registry

# List all addons
minikube addons list
```

---

## 🐳 Part 3: Building Images for Minikube

**Important:** Minikube uses its own Docker daemon. You need to build images inside Minikube.

### Configure Shell to Use Minikube's Docker

```powershell
# Get Docker environment variables
minikube docker-env

# Apply them (PowerShell)
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Verify you're using Minikube's Docker
docker ps  # Should show Minikube containers
```

### Build Images Inside Minikube

```powershell
# Navigate to project root
cd "c:\New Volume (D)\repo\DevOps with AI Antigravity"

# Build backend image
docker build -t ecommerce-backend:v1 ./backend

# Build frontend image  
docker build -t ecommerce-frontend:v1 ./frontend

# Verify images
docker images | Select-String "ecommerce"
```

### Update Kubernetes Manifests for Local Images

Since we're using local images (not from a registry), update the image pull policy:

```powershell
# Create a local version of backend deployment
(Get-Content k8s\04-backend-deployment.yaml) | ForEach-Object {
    $_ -replace 'image: your-registry/ecommerce-backend:v1', 'image: ecommerce-backend:v1' `
       -replace 'imagePullPolicy: Always', 'imagePullPolicy: Never'
} | Set-Content k8s\04-backend-deployment-local.yaml

# Create a local version of frontend deployment
(Get-Content k8s\05-frontend-deployment.yaml) | ForEach-Object {
    $_ -replace 'image: your-registry/ecommerce-frontend:v1', 'image: ecommerce-frontend:v1' `
       -replace 'imagePullPolicy: Always', 'imagePullPolicy: Never' `
       -replace 'type: LoadBalancer', 'type: NodePort'
} | Set-Content k8s\05-frontend-deployment-local.yaml
```

---

## 📦 Part 4: Deploying the Application

### Step 1: Apply Namespace, ConfigMaps & Secrets

```powershell
cd k8s

# Create namespace and configs
kubectl apply -f 01-namespace-config-secrets.yaml

# Verify
kubectl get namespace ecommerce
kubectl get configmap -n ecommerce
kubectl get secret -n ecommerce
```

### Step 2: Deploy PostgreSQL

```powershell
# Deploy PostgreSQL StatefulSet
kubectl apply -f 02-postgres-statefulset.yaml

# Watch PostgreSQL pod start
kubectl get pods -n ecommerce -w
# Press Ctrl+C when postgres-0 is Running

# Check logs
kubectl logs -f postgres-0 -n ecommerce
```

### Step 3: Deploy Redis

```powershell
# Deploy Redis
kubectl apply -f 03-redis-deployment.yaml

# Wait for Redis to be ready
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=120s

# Verify
kubectl get pods -n ecommerce -l app=redis
```

### Step 4: Deploy Backend

```powershell
# Deploy backend (using local image version)
kubectl apply -f 04-backend-deployment-local.yaml

# Wait for backend
kubectl wait --for=condition=ready pod -l app=backend -n ecommerce --timeout=180s

# Check logs
kubectl logs -f -l app=backend -n ecommerce
```

### Step 5: Deploy Frontend

```powershell
# Deploy frontend (using local image version)
kubectl apply -f 05-frontend-deployment-local.yaml

# Wait for frontend
kubectl wait --for=condition=ready pod -l app=frontend -n ecommerce --timeout=120s
```

---

## ✅ Part 5: Verifying the Deployment

### Check All Resources

```powershell
# Get all resources
kubectl get all -n ecommerce

# Expected output:
# - StatefulSet: postgres (1/1)
# - Deployment: redis (1/1)
# - Deployment: backend (3/3)
# - Deployment: frontend (3/3)
# - Services: postgres, redis, backend, frontend
```

### Verify Each Component

#### 1. PostgreSQL

```powershell
# Check pod status
kubectl get statefulset postgres -n ecommerce

# Check PVC
kubectl get pvc -n ecommerce

# Connect to database
kubectl exec -it postgres-0 -n ecommerce -- psql -U postgres -d ecommerce_db

# Inside psql:
\dt  # List tables
SELECT COUNT(*) FROM products;  # Check seed data
\q  # Exit
```

#### 2. Redis

```powershell
# Check Redis pod
kubectl get pods -l app=redis -n ecommerce

# Test Redis connection
kubectl exec -it $(kubectl get pod -n ecommerce -l app=redis -o jsonpath='{.items[0].metadata.name}') -n ecommerce -- redis-cli ping
# Should return: PONG
```

#### 3. Backend

```powershell
# Check backend pods
kubectl get pods -l app=backend -n ecommerce

# Test health endpoint
kubectl exec -it $(kubectl get pod -n ecommerce -l app=backend -o jsonpath='{.items[0].metadata.name}') -n ecommerce -- wget -qO- http://localhost:5000/health

# Should return JSON with status: healthy
```

#### 4. Frontend

```powershell
# Check frontend pods
kubectl get pods -l app=frontend -n ecommerce

# Test nginx
kubectl exec -it $(kubectl get pod -n ecommerce -l app=frontend -o jsonpath='{.items[0].metadata.name}') -n ecommerce -- wget -qO- http://localhost/health

# Should return: healthy
```

---

## 🌐 Part 6: Accessing the Application

### Method 1: Port Forwarding (Easiest)

```powershell
# Forward backend
kubectl port-forward svc/backend 5000:5000 -n ecommerce

# In a new terminal, forward frontend
kubectl port-forward svc/frontend 3000:80 -n ecommerce
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Method 2: NodePort Service

```powershell
# Get NodePort
kubectl get svc frontend -n ecommerce

# Get Minikube IP
minikube ip

# Access application
# http://<minikube-ip>:<node-port>
```

### Method 3: Minikube Service (Recommended)

```powershell
# Open frontend in browser
minikube service frontend -n ecommerce

# This automatically opens your default browser
```

### Method 4: Minikube Tunnel (For LoadBalancer)

```powershell
# In a separate terminal (requires admin)
minikube tunnel

# Get external IP
kubectl get svc frontend -n ecommerce

# Access via external IP
# http://<external-ip>
```

---

## 🐛 Part 7: Common Debugging Commands

### Pod Management

```powershell
# List all pods
kubectl get pods -n ecommerce

# Get detailed pod info
kubectl describe pod <pod-name> -n ecommerce

# View pod logs
kubectl logs <pod-name> -n ecommerce

# Follow logs (real-time)
kubectl logs -f <pod-name> -n ecommerce

# Previous container logs (if crashed)
kubectl logs <pod-name> -n ecommerce --previous

# Logs from specific container
kubectl logs <pod-name> -c <container-name> -n ecommerce

# Execute command in pod
kubectl exec -it <pod-name> -n ecommerce -- /bin/sh

# Get pod YAML
kubectl get pod <pod-name> -n ecommerce -o yaml
```

### Service and Network Debugging

```powershell
# List services
kubectl get svc -n ecommerce

# Describe service
kubectl describe svc <service-name> -n ecommerce

# Get endpoints
kubectl get endpoints -n ecommerce

# Test service connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -n ecommerce -- sh
# Inside container:
wget -O- http://backend:5000/health
exit
```

### Resource Usage

```powershell
# View resource usage (requires metrics-server)
kubectl top nodes
kubectl top pods -n ecommerce

# View HPA status
kubectl get hpa -n ecommerce
kubectl describe hpa backend-hpa -n ecommerce
```

### Events and Troubleshooting

```powershell
# View cluster events
kubectl get events -n ecommerce

# Sort events by timestamp
kubectl get events -n ecommerce --sort-by='.lastTimestamp'

# Watch events
kubectl get events -n ecommerce --watch

# Describe problematic pod
kubectl describe pod <pod-name> -n ecommerce
```

### ConfigMaps and Secrets

```powershell
# View ConfigMap
kubectl get configmap ecommerce-config -n ecommerce -o yaml

# View Secret (base64 encoded)
kubectl get secret ecommerce-secrets -n ecommerce -o yaml

# Decode secret value
kubectl get secret ecommerce-secrets -n ecommerce -o jsonpath='{.data.SECRET_KEY}' | base64 -d
```

### Storage

```powershell
# List PVCs
kubectl get pvc -n ecommerce

# Describe PVC
kubectl describe pvc <pvc-name> -n ecommerce

# List PVs
kubectl get pv
```

---

## 🔄 Part 8: Making Changes and Updates

### Update ConfigMap

```powershell
# Edit ConfigMap
kubectl edit configmap ecommerce-config -n ecommerce

# Or update file and reapply
kubectl apply -f 01-namespace-config-secrets.yaml

# Restart pods to pick up changes
kubectl rollout restart deployment/backend -n ecommerce
kubectl rollout restart deployment/frontend -n ecommerce
```

### Rebuild and Redeploy Application

```powershell
# 1. Ensure you're using Minikube's Docker
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 2. Rebuild images
docker build -t ecommerce-backend:v2 ./backend
docker build -t ecommerce-frontend:v2 ./frontend

# 3. Update deployment
kubectl set image deployment/backend backend=ecommerce-backend:v2 -n ecommerce
kubectl set image deployment/frontend frontend=ecommerce-frontend:v2 -n ecommerce

# 4. Watch rollout
kubectl rollout status deployment/backend -n ecommerce
kubectl rollout status deployment/frontend -n ecommerce

# 5. Rollback if needed
kubectl rollout undo deployment/backend -n ecommerce
```

### Scale Deployments

```powershell
# Scale backend
kubectl scale deployment backend --replicas=5 -n ecommerce

# Scale frontend
kubectl scale deployment frontend --replicas=2 -n ecommerce

# Verify
kubectl get deployments -n ecommerce
```

---

## 🔧 Common Issues and Solutions

### Issue 1: Pods Stuck in ImagePullBackOff

**Cause:** Minikube can't find the image

**Solution:**
```powershell
# Make sure you built images in Minikube's Docker
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
docker images  # Should show your images

# Rebuild if needed
docker build -t ecommerce-backend:v1 ./backend
docker build -t ecommerce-frontend:v1 ./frontend

# Update imagePullPolicy to Never
kubectl edit deployment backend -n ecommerce
# Change imagePullPolicy from Always to Never
```

### Issue 2: Pods CrashLoopBackOff

**Cause:** Application failing to start

**Solution:**
```powershell
# Check logs
kubectl logs <pod-name> -n ecommerce --previous

# Common causes:
# - Database connection failed (check postgres is running)
# - Missing environment variables (check configmap/secrets)
# - Application error (check code)

# Describe pod for events
kubectl describe pod <pod-name> -n ecommerce
```

### Issue 3: Can't Access Application

**Cause:** Service or port-forward not working

**Solution:**
```powershell
# Check service exists
kubectl get svc -n ecommerce

# Use minikube service
minikube service frontend -n ecommerce

# Or use port-forward
kubectl port-forward svc/frontend 3000:80 -n ecommerce
```

### Issue 4: Database Not Persisting Data

**Cause:** PVC not bound or lost data

**Solution:**
```powershell
# Check PVC status
kubectl get pvc -n ecommerce

# Should be Bound, not Pending

# Check PV
kubectl get pv

# If Pending, check storage class
kubectl get storageclass

# Recreate StatefulSet if needed
kubectl delete statefulset postgres -n ecommerce
kubectl apply -f 02-postgres-statefulset.yaml
```

### Issue 5: Minikube Out of Resources

**Cause:** Not enough CPU/memory allocated

**Solution:**
```powershell
# Stop Minikube
minikube stop

# Delete and recreate with more resources
minikube delete
minikube start --driver=docker --cpus=6 --memory=8192

# Or increase resources
minikube config set cpus 6
minikube config set memory 8192
minikube start
```

---

## 🧹 Cleanup

### Delete Application

```powershell
# Delete namespace (removes everything)
kubectl delete namespace ecommerce

# Or delete individual resources
kubectl delete -f k8s/05-frontend-deployment-local.yaml
kubectl delete -f k8s/04-backend-deployment-local.yaml
kubectl delete -f k8s/03-redis-deployment.yaml
kubectl delete -f k8s/02-postgres-statefulset.yaml
kubectl delete -f k8s/01-namespace-config-secrets.yaml
```

### Stop Minikube

```powershell
# Stop cluster (preserves state)
minikube stop

# Delete cluster (removes everything)
minikube delete

# Delete all profiles
minikube delete --all
```

---

## 📊 Useful Dashboard

### Kubernetes Dashboard

```powershell
# Enable dashboard addon
minikube addons enable dashboard

# Open dashboard
minikube dashboard

# Or get dashboard URL
minikube dashboard --url
```

---

## 🎯 Quick Testing Workflow

Here's a complete workflow for testing changes:

```powershell
# 1. Start Minikube
minikube start

# 2. Use Minikube's Docker
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 3. Build images
cd "c:\New Volume (D)\repo\DevOps with AI Antigravity"
docker build -t ecommerce-backend:v1 ./backend
docker build -t ecommerce-frontend:v1 ./frontend

# 4. Deploy application
cd k8s
kubectl apply -f 01-namespace-config-secrets.yaml
kubectl apply -f 02-postgres-statefulset.yaml
kubectl apply -f 03-redis-deployment.yaml
kubectl apply -f 04-backend-deployment-local.yaml
kubectl apply -f 05-frontend-deployment-local.yaml

# 5. Wait for pods
kubectl get pods -n ecommerce -w

# 6. Access application
minikube service frontend -n ecommerce

# 7. View logs
kubectl logs -f -l app=backend -n ecommerce

# 8. Test changes
# Make changes to code, then:
docker build -t ecommerce-backend:v2 ./backend
kubectl set image deployment/backend backend=ecommerce-backend:v2 -n ecommerce

# 9. Cleanup when done
kubectl delete namespace ecommerce
minikube stop
```

---

## 📚 Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes Debugging Guide](https://kubernetes.io/docs/tasks/debug/)
- [Minikube Addons List](https://minikube.sigs.k8s.io/docs/commands/addons/)

---

**Your local Kubernetes testing environment is ready!** 🚀

For production deployment to cloud providers (GKE, EKS, AKS), see the main [README.md](./README.md).
