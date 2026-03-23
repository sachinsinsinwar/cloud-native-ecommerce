# Minikube Local Testing on Ubuntu WSL2

Complete guide for installing and testing your Kubernetes e-commerce application using Ubuntu WSL2 on Windows (without Chocolatey).

---

## 📋 Prerequisites

- **Windows 10/11** with WSL2 enabled
- **Ubuntu** installed in WSL2
- **At least 4GB RAM** available for Minikube
- **At least 20GB free disk space**

---

## 🔧 Part 1: Setting Up Ubuntu WSL2

### Verify WSL2 is Installed

Open PowerShell (Windows) as Administrator:

```powershell
# Check WSL version
wsl --list --verbose

# Should show Ubuntu with VERSION 2
# If VERSION is 1, upgrade to WSL2:
wsl --set-version Ubuntu 2
```

### Open Ubuntu Terminal

```powershell
# From PowerShell or Windows Terminal
wsl
```

All commands below should be run in Ubuntu WSL terminal unless specified otherwise.

---

## 🐳 Part 2: Install Docker on Ubuntu WSL2

### Update Package Repository

```bash
sudo apt update
sudo apt upgrade -y
```

### Install Docker

```bash
# Install prerequisites
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index
sudo apt update

# Install Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Verify Docker installation
docker --version
```

### Configure Docker (Important!)

```bash
# Add your user to docker group (avoid using sudo)
sudo usermod -aG docker $USER

# Start Docker service
sudo service docker start

# Enable Docker to start on WSL launch (add to ~/.bashrc)
echo 'sudo service docker start > /dev/null 2>&1' >> ~/.bashrc

# Apply group changes (or restart WSL)
newgrp docker

# Test Docker without sudo
docker run hello-world
```

**If Docker fails to start:**
```bash
# Check Docker daemon status
sudo service docker status

# Manually start if needed
sudo service docker start

# Check logs if issues persist
sudo journalctl -u docker
```

---

## ⚙️ Part 3: Install kubectl

```bash
# Download latest kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Make it executable
chmod +x kubectl

# Move to PATH
sudo mv kubectl /usr/local/bin/

# Verify installation
kubectl version --client

# Expected output: Client Version: v1.28.x
```

---

## 🚀 Part 4: Install Minikube

```bash
# Download Minikube binary
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64

# Install Minikube
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Remove downloaded file
rm minikube-linux-amd64

# Verify installation
minikube version
```

---

## 🎯 Part 5: Start Minikube Cluster

### Start Minikube with Docker Driver

```bash
# Start Minikube (this may take 3-5 minutes first time)
minikube start --driver=docker --cpus=4 --memory=4096

# Expected output:
# ✓ minikube v1.x.x on Ubuntu
# ✓ Using the docker driver based on user configuration
# ✓ Starting control plane node minikube in cluster minikube
# ✓ Done! kubectl is now configured to use "minikube" cluster
```

### Verify Cluster is Running

```bash
# Check Minikube status
minikube status

# Should show:
# minikube: Running
# kubelet: Running
# apiserver: Running

# Check cluster info
kubectl cluster-info

# Check nodes
kubectl get nodes
```

### Enable Required Addons

```bash
# Enable metrics-server (required for autoscaling)
minikube addons enable metrics-server

# Enable ingress (optional, for ingress testing)
minikube addons enable ingress

# List all enabled addons
minikube addons list
```

---

## 🐳 Part 6: Build Container Images

### Navigate to Project Directory

**Important:** Access your Windows files from WSL:

```bash
# Your Windows C: drive is mounted at /mnt/c/
cd "/mnt/c/New Volume (D)/repo/DevOps with AI Antigravity"

# Verify you're in the right place
ls -la
# Should see: backend/, frontend/, k8s/, docker-compose.yml, etc.
```

### Configure Docker to Use Minikube's Daemon

```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify you're using Minikube's Docker
docker ps
# Should show Minikube containers (k8s_kube-apiserver, etc.)
```

**Important:** This setting is per-shell session. If you open a new terminal, run `eval $(minikube docker-env)` again.

### Build Backend Image

```bash
# Build backend
docker build -t ecommerce-backend:v1 ./backend

# Verify image
docker images | grep ecommerce-backend
```

### Build Frontend Image

```bash
# Build frontend
docker build -t ecommerce-frontend:v1 ./frontend

# Verify image
docker images | grep ecommerce-frontend
```

**Tip:** Add this to your `~/.bashrc` for convenience:
```bash
echo 'alias minikube-docker="eval \$(minikube docker-env)"' >> ~/.bashrc
source ~/.bashrc
# Now you can just run: minikube-docker
```

---

## 📝 Part 7: Prepare Kubernetes Manifests for Local Deployment

### Create Local Deployment Files

```bash
cd k8s

# Create local version of backend deployment
sed 's|image: your-registry/ecommerce-backend:v1|image: ecommerce-backend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g' \
    04-backend-deployment.yaml > 04-backend-deployment-local.yaml

# Create local version of frontend deployment
sed 's|image: your-registry/ecommerce-frontend:v1|image: ecommerce-frontend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g; s|type: LoadBalancer|type: NodePort|g' \
    05-frontend-deployment.yaml > 05-frontend-deployment-local.yaml

# Verify files were created
ls -lh *-local.yaml
```

---

## 🚀 Part 8: Deploy Application to Minikube

### Step-by-Step Deployment

```bash
# Make sure you're in the k8s directory
cd "/mnt/c/New Volume (D)/repo/DevOps with AI Antigravity/k8s"

# 1. Create namespace, ConfigMaps, and Secrets
kubectl apply -f 01-namespace-config-secrets.yaml

# Verify
kubectl get namespace ecommerce
kubectl get configmap -n ecommerce
kubectl get secret -n ecommerce

# 2. Deploy PostgreSQL
kubectl apply -f 02-postgres-statefulset.yaml

# Wait for PostgreSQL to be ready (may take 1-2 minutes)
echo "Waiting for PostgreSQL..."
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce --timeout=300s

# Check PostgreSQL logs
kubectl logs postgres-0 -n ecommerce --tail=20

# 3. Deploy Redis
kubectl apply -f 03-redis-deployment.yaml

# Wait for Redis
echo "Waiting for Redis..."
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=120s

# 4. Deploy Backend
kubectl apply -f 04-backend-deployment-local.yaml

# Wait for Backend
echo "Waiting for Backend..."
kubectl wait --for=condition=ready pod -l app=backend -n ecommerce --timeout=180s

# Check backend logs
kubectl logs -l app=backend -n ecommerce --tail=30

# 5. Deploy Frontend
kubectl apply -f 05-frontend-deployment-local.yaml

# Wait for Frontend
echo "Waiting for Frontend..."
kubectl wait --for=condition=ready pod -l app=frontend -n ecommerce --timeout=120s

# 6. Verify all pods are running
kubectl get pods -n ecommerce
```

**Expected Output:**
```
NAME                        READY   STATUS    RESTARTS   AGE
postgres-0                  1/1     Running   0          2m
redis-XXXXXXXXX-XXXXX       1/1     Running   0          1m
backend-XXXXXXXXX-XXXXX     1/1     Running   0          1m
backend-XXXXXXXXX-XXXXX     1/1     Running   0          1m
backend-XXXXXXXXX-XXXXX     1/1     Running   0          1m
frontend-XXXXXXXXX-XXXXX    1/1     Running   0          30s
frontend-XXXXXXXXX-XXXXX    1/1     Running   0          30s
frontend-XXXXXXXXX-XXXXX    1/1     Running   0          30s
```

### View All Resources

```bash
# Get all resources in namespace
kubectl get all -n ecommerce

# Get detailed information
kubectl get pods,svc,statefulset,deployment,pvc -n ecommerce
```

---

## 🌐 Part 9: Access the Application

### Method 1: Minikube Service (Easiest)

```bash
# Get the URL for frontend service
minikube service frontend -n ecommerce --url

# Example output: http://192.168.49.2:30123
```

**Open this URL in your Windows browser!**

### Method 2: Port Forwarding

```bash
# Forward frontend to localhost:3000
kubectl port-forward svc/frontend 3000:80 -n ecommerce

# In another terminal, forward backend (optional, for API testing)
kubectl port-forward svc/backend 5000:5000 -n ecommerce
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Method 3: NodePort

```bash
# Get Minikube IP
minikube ip

# Get NodePort
kubectl get svc frontend -n ecommerce -o jsonpath='{.spec.ports[0].nodePort}'

# Construct URL
echo "http://$(minikube ip):$(kubectl get svc frontend -n ecommerce -o jsonpath='{.spec.ports[0].nodePort}')"
```

---

## ✅ Part 10: Verify Deployment

### Check PostgreSQL

```bash
# Connect to PostgreSQL
kubectl exec -it postgres-0 -n ecommerce -- psql -U postgres -d ecommerce_db

# Inside psql:
\dt                          # List tables
SELECT COUNT(*) FROM products;  # Check seed data (should be 5)
SELECT name, price FROM products LIMIT 3;  # View products
\q                          # Exit
```

### Check Redis

```bash
# Test Redis connection
kubectl exec -it $(kubectl get pod -n ecommerce -l app=redis -o jsonpath='{.items[0].metadata.name}') -n ecommerce -- redis-cli ping

# Should return: PONG
```

### Check Backend API

```bash
# Test health endpoint
kubectl exec -it $(kubectl get pod -n ecommerce -l app=backend -o jsonpath='{.items[0].metadata.name}') -n ecommerce -- wget -qO- http://localhost:5000/health | jq

# Should return:
# {
#   "status": "healthy",
#   "checks": {
#     "database": "connected",
#     "redis": "connected"
#   }
# }
```

### Check Frontend

```bash
# Test nginx health
kubectl exec -it $(kubectl get pod -n ecommerce -l app=frontend -o jsonpath='{.items[0].metadata.name}') -n ecommerce -- wget -qO- http://localhost/health

# Should return: healthy
```

---

## 🐛 Part 11: Common Debugging Commands

### Pod Management

```bash
# List all pods
kubectl get pods -n ecommerce

# Describe pod (shows events, issues)
kubectl describe pod <pod-name> -n ecommerce

# View logs
kubectl logs <pod-name> -n ecommerce

# Follow logs (real-time)
kubectl logs -f <pod-name> -n ecommerce

# Previous container logs (if crashed)
kubectl logs <pod-name> -n ecommerce --previous

# All backend pod logs
kubectl logs -l app=backend -n ecommerce --tail=50

# Execute command in pod
kubectl exec -it <pod-name> -n ecommerce -- /bin/sh
```

### Service Debugging

```bash
# List services
kubectl get svc -n ecommerce

# Describe service
kubectl describe svc backend -n ecommerce

# Get service endpoints
kubectl get endpoints -n ecommerce

# Test service connectivity from within cluster
kubectl run -it --rm debug --image=busybox --restart=Never -n ecommerce -- sh
# Inside container:
wget -O- http://backend:5000/health
exit
```

### Resource Monitoring

```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n ecommerce

# View HPA status
kubectl get hpa -n ecommerce
kubectl describe hpa backend-hpa -n ecommerce
```

### Events and Troubleshooting

```bash
# View events (last hour)
kubectl get events -n ecommerce --sort-by='.lastTimestamp'

# Watch events
kubectl get events -n ecommerce --watch

# Get all cluster events
kubectl get events --all-namespaces
```

### ConfigMaps and Secrets

```bash
# View ConfigMap
kubectl get configmap ecommerce-config -n ecommerce -o yaml

# Edit ConfigMap
kubectl edit configmap ecommerce-config -n ecommerce

# After editing, restart pods
kubectl rollout restart deployment/backend -n ecommerce
kubectl rollout restart deployment/frontend -n ecommerce

# View Secret (base64 encoded)
kubectl get secret ecommerce-secrets -n ecommerce -o yaml

# Decode secret value
kubectl get secret ecommerce-secrets -n ecommerce -o jsonpath='{.data.SECRET_KEY}' | base64 -d
echo  # newline
```

---

## 🔄 Part 12: Making Changes and Redeploying

### Update Application Code

```bash
# 1. Make changes to your code in Windows
# Edit files in: C:\New Volume (D)\repo\DevOps with AI Antigravity\

# 2. In WSL, configure Docker for Minikube
eval $(minikube docker-env)

# 3. Navigate to project
cd "/mnt/c/New Volume (D)/repo/DevOps with AI Antigravity"

# 4. Rebuild image (backend example)
docker build -t ecommerce-backend:v2 ./backend

# 5. Update deployment
kubectl set image deployment/backend backend=ecommerce-backend:v2 -n ecommerce

# 6. Watch rollout
kubectl rollout status deployment/backend -n ecommerce

# 7. Verify new pods
kubectl get pods -n ecommerce -l app=backend

# 8. Rollback if needed
kubectl rollout undo deployment/backend -n ecommerce
```

### Scale Deployments

```bash
# Scale backend to 5 replicas
kubectl scale deployment backend --replicas=5 -n ecommerce

# Scale frontend to 2 replicas
kubectl scale deployment frontend --replicas=2 -n ecommerce

# Verify
kubectl get deployments -n ecommerce
```

---

## 🧹 Part 13: Cleanup

### Delete Application

```bash
# Delete entire namespace (removes everything)
kubectl delete namespace ecommerce

# Or delete resources individually
kubectl delete -f 05-frontend-deployment-local.yaml
kubectl delete -f 04-backend-deployment-local.yaml
kubectl delete -f 03-redis-deployment.yaml
kubectl delete -f 02-postgres-statefulset.yaml
kubectl delete -f 01-namespace-config-secrets.yaml
```

### Stop Minikube

```bash
# Stop cluster (preserves state)
minikube stop

# Start again later
minikube start

# Delete cluster (removes everything)
minikube delete

# Delete all Minikube profiles
minikube delete --all
```

### Clean Up Docker Images

```bash
# Configure Docker for Minikube
eval $(minikube docker-env)

# Remove old images
docker rmi ecommerce-backend:v1
docker rmi ecommerce-frontend:v1

# Clean up unused images
docker image prune -a
```

---

## 🚨 Common Issues and Solutions

### Issue 1: "Cannot connect to Docker daemon"

**Solution:**
```bash
# Start Docker service
sudo service docker start

# Check status
sudo service docker status

# If still fails, restart WSL
# In PowerShell (Windows):
wsl --shutdown
# Then reopen Ubuntu
```

### Issue 2: "Pods stuck in ImagePullBackOff"

**Solution:**
```bash
# Make sure you're using Minikube's Docker
eval $(minikube docker-env)

# Verify images exist
docker images | grep ecommerce

# Rebuild if missing
docker build -t ecommerce-backend:v1 ./backend
docker build -t ecommerce-frontend:v1 ./frontend

# Ensure imagePullPolicy is Never in local manifests
grep imagePullPolicy k8s/*-local.yaml
```

### Issue 3: "Pods in CrashLoopBackOff"

**Solution:**
```bash
# Check pod logs
kubectl logs <pod-name> -n ecommerce --previous

# Common causes:
# - Database not ready: Check postgres pod
# - Wrong env vars: Check configmap/secrets
# - Application error: Check logs

# Describe pod for events
kubectl describe pod <pod-name> -n ecommerce
```

### Issue 4: "Can't access application from Windows browser"

**Solution:**
```bash
# Make sure Minikube is running
minikube status

# Use minikube service command (automatically opens browser)
minikube service frontend -n ecommerce

# Or use port-forward
kubectl port-forward svc/frontend 3000:80 -n ecommerce
# Then access: http://localhost:3000
```

### Issue 5: "Permission denied" errors

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes
newgrp docker

# Or restart WSL:
# In PowerShell: wsl --shutdown
# Then reopen Ubuntu

# Test Docker without sudo
docker ps
```

### Issue 6: "Minikube won't start"

**Solution:**
```bash
# Check Docker is running
docker ps

# Delete and recreate cluster
minikube delete
minikube start --driver=docker --cpus=4 --memory=4096

# Check logs for specific errors
minikube logs
```

---

## 📊 Part 14: Kubernetes Dashboard

### Enable and Access Dashboard

```bash
# Enable dashboard addon
minikube addons enable dashboard

# Start dashboard (opens in browser)
minikube dashboard

# Or get URL to open manually
minikube dashboard --url
# Copy URL and paste in Windows browser
```

---

## 🎯 Complete Testing Workflow

Here's the complete workflow to test your application:

```bash
#!/bin/bash
# Save this as: deploy-local.sh

echo "🚀 Starting E-Commerce Deployment on Minikube"

# 1. Start Minikube (if not running)
echo "📦 Starting Minikube..."
minikube start --driver=docker --cpus=4 --memory=4096

# 2. Enable addons
echo "🔧 Enabling addons..."
minikube addons enable metrics-server

# 3. Configure Docker
echo "🐳 Configuring Docker for Minikube..."
eval $(minikube docker-env)

# 4. Navigate to project
echo "📂 Navigating to project..."
cd "/mnt/c/New Volume (D)/repo/DevOps with AI Antigravity"

# 5. Build images
echo "🏗️  Building backend image..."
docker build -t ecommerce-backend:v1 ./backend

echo "🏗️  Building frontend image..."
docker build -t ecommerce-frontend:v1 ./frontend

# 6. Create local manifests
echo "📝 Creating local manifests..."
cd k8s
sed 's|image: your-registry/ecommerce-backend:v1|image: ecommerce-backend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g' \
    04-backend-deployment.yaml > 04-backend-deployment-local.yaml
sed 's|image: your-registry/ecommerce-frontend:v1|image: ecommerce-frontend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g; s|type: LoadBalancer|type: NodePort|g' \
    05-frontend-deployment.yaml > 05-frontend-deployment-local.yaml

# 7. Deploy to Kubernetes
echo "☸️  Deploying to Kubernetes..."
kubectl apply -f 01-namespace-config-secrets.yaml
sleep 2

echo "🗄️  Deploying PostgreSQL..."
kubectl apply -f 02-postgres-statefulset.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce --timeout=300s

echo "📮 Deploying Redis..."
kubectl apply -f 03-redis-deployment.yaml
kubectl wait --for=condition=ready pod -l app=redis -n ecommerce --timeout=120s

echo "🔌 Deploying Backend..."
kubectl apply -f 04-backend-deployment-local.yaml
kubectl wait --for=condition=ready pod -l app=backend -n ecommerce --timeout=180s

echo "🎨 Deploying Frontend..."
kubectl apply -f 05-frontend-deployment-local.yaml
kubectl wait --for=condition=ready pod -l app=frontend -n ecommerce --timeout=120s

# 8. Show status
echo ""
echo "✅ Deployment complete!"
echo ""
kubectl get all -n ecommerce

# 9. Get access URL
echo ""
echo "🌐 Access your application:"
echo "Run: minikube service frontend -n ecommerce"
echo ""
echo "Or visit: http://$(minikube ip):$(kubectl get svc frontend -n ecommerce -o jsonpath='{.spec.ports[0].nodePort}')"
```

**Make it executable and run:**
```bash
chmod +x deploy-local.sh
./deploy-local.sh
```

---

## 📚 Useful Aliases

Add these to your `~/.bashrc`:

```bash
# Add to ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# Minikube aliases
alias k='kubectl'
alias kgp='kubectl get pods -n ecommerce'
alias kgs='kubectl get svc -n ecommerce'
alias kga='kubectl get all -n ecommerce'
alias kl='kubectl logs -f -n ecommerce'
alias kd='kubectl describe -n ecommerce'
alias ke='kubectl exec -it -n ecommerce'
alias mk='minikube'
alias mks='minikube status'
alias mkd='eval $(minikube docker-env)'

# Docker aliases
alias dps='docker ps'
alias di='docker images'
alias dl='docker logs'

# Common commands
alias start-docker='sudo service docker start'
alias pods='kubectl get pods -n ecommerce'
alias logs='kubectl logs -f -l app=backend -n ecommerce'
EOF

# Reload
source ~/.bashrc
```

---

## 🎓 Next Steps

1. **Test the application** - Sign up, login, browse products
2. **Check logs** - Monitor application behavior
3. **Make changes** - Update code and redeploy
4. **Scale services** - Test autoscaling
5. **Break things** - Kill pods and watch Kubernetes heal
6. **Explore dashboard** - Visualize your cluster

---

## 📖 Additional Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [WSL2 Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [Docker on WSL2](https://docs.docker.com/desktop/windows/wsl/)

---

**You're all set to test Kubernetes locally on Ubuntu WSL!** 🚀
