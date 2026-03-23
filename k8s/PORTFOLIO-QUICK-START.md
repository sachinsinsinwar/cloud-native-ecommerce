# Quick Kubernetes Setup for Portfolio/Showcase

**Goal:** Get your e-commerce app running on Kubernetes (Minikube) to demonstrate K8s skills.

**You already have:** Docker running in WSL ✅

**What you'll add:** kubectl + Minikube + Your app on K8s

---

## ⚡ Super Quick Start (Copy & Paste)

Open **Ubuntu WSL** terminal and run these commands:

### Step 1: Install kubectl and Minikube

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client

# Install Minikube  
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64
minikube version
```

### Step 2: Start Minikube

```bash
# Start Kubernetes cluster
minikube start --driver=docker --cpus=4 --memory=4096

# Enable metrics for autoscaling demo
minikube addons enable metrics-server

# Verify it's running
kubectl get nodes
```

### Step 3: Build Images in Minikube

```bash
# Point to Minikube's Docker
eval $(minikube docker-env)

# Navigate to your project
cd "/mnt/c/New Volume (D)/repo/DevOps with AI Antigravity"

# Build images
docker build -t ecommerce-backend:v1 ./backend
docker build -t ecommerce-frontend:v1 ./frontend

# Verify
docker images | grep ecommerce
```

### Step 4: Create Local K8s Manifests

```bash
cd k8s

# Create backend local manifest
sed 's|image: your-registry/ecommerce-backend:v1|image: ecommerce-backend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g' \
    04-backend-deployment.yaml > 04-backend-deployment-local.yaml

# Create frontend local manifest  
sed 's|image: your-registry/ecommerce-frontend:v1|image: ecommerce-frontend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g; s|type: LoadBalancer|type: NodePort|g' \
    05-frontend-deployment.yaml > 05-frontend-deployment-local.yaml
```

### Step 5: Deploy to Kubernetes

```bash
# Deploy everything in order
kubectl apply -f 01-namespace-config-secrets.yaml
kubectl apply -f 02-postgres-statefulset.yaml
kubectl apply -f 03-redis-deployment.yaml
kubectl apply -f 04-backend-deployment-local.yaml
kubectl apply -f 05-frontend-deployment-local.yaml

# Wait for everything to be ready (2-3 minutes)
kubectl get pods -n ecommerce -w
# Press Ctrl+C when all pods show 1/1 Running
```

### Step 6: Access Your K8s App

```bash
# Get the URL
minikube service frontend -n ecommerce --url

# Or open in browser automatically
minikube service frontend -n ecommerce
```

---

## 🎬 Demo Script for Interviews/Showcase

Here's what to show when demonstrating your Kubernetes knowledge:

### 1. Show Cluster Status

```bash
# Show cluster info
kubectl cluster-info

# Show nodes
kubectl get nodes

# Show all namespaces
kubectl get namespaces
```

**Say:** "I've deployed a microservices e-commerce application on a local Kubernetes cluster using Minikube."

### 2. Show Your Deployments

```bash
# Show all resources
kubectl get all -n ecommerce

# Show deployments
kubectl get deployments -n ecommerce
```

**Say:** "The application consists of 4 main components: PostgreSQL StatefulSet for persistent data, Redis for caching, a Flask backend API, and a React frontend."

### 3. Demonstrate StatefulSet (Database)

```bash
# Show StatefulSet
kubectl get statefulset -n ecommerce

# Show PVC (Persistent Volume Claim)
kubectl get pvc -n ecommerce

# Show that data persists
kubectl exec -it postgres-0 -n ecommerce -- psql -U postgres -d ecommerce_db -c "SELECT COUNT(*) FROM products;"
```

**Say:** "I used a StatefulSet for PostgreSQL to ensure data persistence and stable network identity, with a PersistentVolumeClaim for storage."

### 4. Demonstrate Scaling

```bash
# Show current replicas
kubectl get deployment backend -n ecommerce

# Scale backend to 5 replicas
kubectl scale deployment backend --replicas=5 -n ecommerce

# Watch pods being created
kubectl get pods -n ecommerce -w

# Scale back down
kubectl scale deployment backend --replicas=3 -n ecommerce
```

**Say:** "Kubernetes makes horizontal scaling easy - I can scale from 3 to 5 backend replicas with a single command."

### 5. Demonstrate Self-Healing

```bash
# Delete a pod
kubectl delete pod -l app=backend -n ecommerce --force --grace-period=0 | head -1

# Watch it automatically recreate
kubectl get pods -n ecommerce -w
```

**Say:** "Kubernetes provides self-healing - if a pod crashes, it's automatically recreated to maintain the desired state."

### 6. Show Autoscaling Configuration

```bash
# Show HPA (Horizontal Pod Autoscaler)
kubectl get hpa -n ecommerce

# Describe HPA
kubectl describe hpa backend-hpa -n ecommerce
```

**Say:** "I've configured Horizontal Pod Autoscaling based on CPU and memory metrics, which automatically scales between 2 and 10 replicas."

### 7. Demonstrate Service Discovery

```bash
# Show services
kubectl get svc -n ecommerce

# Show how backend connects to postgres
kubectl exec -it $(kubectl get pod -n ecommerce -l app=backend -o jsonpath='{.items[0].metadata.name}') -n ecommerce -- env | grep DATABASE_URL
```

**Say:** "Services enable internal DNS-based service discovery - the backend connects to postgres using the service name, not IP addresses."

### 8. Show ConfigMaps and Secrets

```bash
# Show ConfigMap
kubectl get configmap ecommerce-config -n ecommerce -o yaml

# Show Secrets (without exposing values)
kubectl get secrets -n ecommerce
```

**Say:** "I use ConfigMaps for non-sensitive configuration and Secrets for sensitive data like passwords, following security best practices."

### 9. Demonstrate Rolling Updates

```bash
# Update backend image
kubectl set image deployment/backend backend=ecommerce-backend:v2 -n ecommerce

# Watch the rolling update
kubectl rollout status deployment/backend -n ecommerce

# View rollout history
kubectl rollout history deployment/backend -n ecommerce

# Rollback if needed
kubectl rollout undo deployment/backend -n ecommerce
```

**Say:** "Kubernetes enables zero-downtime deployments with rolling updates, and easy rollbacks if needed."

### 10. Show Resource Management

```bash
# Show resource usage
kubectl top nodes
kubectl top pods -n ecommerce

# Describe a deployment to show resource limits
kubectl describe deployment backend -n ecommerce | grep -A 5 "Limits"
```

**Say:** "I've configured resource requests and limits to ensure efficient cluster resource utilization."

---

## 📊 Visual Demo with Dashboard

```bash
# Enable dashboard
minikube addons enable dashboard

# Open dashboard
minikube dashboard
```

**This opens a visual interface showing:**
- All your pods, deployments, services
- Resource usage graphs
- Logs viewer
- Easy navigation of your cluster

**Perfect for visual demonstrations!**

---

## 🎯 Key Kubernetes Concepts You Can Showcase

Based on your manifests, you demonstrate knowledge of:

### Core Concepts
✅ **Pods** - Basic unit of deployment  
✅ **Deployments** - Managing stateless applications  
✅ **StatefulSets** - Managing stateful applications  
✅ **Services** - Network access and service discovery  
✅ **Namespaces** - Resource isolation

### Configuration
✅ **ConfigMaps** - Configuration management  
✅ **Secrets** - Sensitive data management  
✅ **Environment Variables** - App configuration

### Storage
✅ **PersistentVolumes** - Persistent storage  
✅ **PersistentVolumeClaims** - Storage requests  
✅ **StorageClasses** - Dynamic provisioning

### Scaling & Availability
✅ **Horizontal Pod Autoscaler** - Auto-scaling  
✅ **Pod Disruption Budgets** - High availability  
✅ **Replica Sets** - Desired state management

### Networking
✅ **ClusterIP Services** - Internal communication  
✅ **NodePort Services** - External access  
✅ **Ingress** - HTTP routing (configured)

### Best Practices
✅ **Health Probes** - Liveness, readiness, startup  
✅ **Resource Limits** - CPU and memory management  
✅ **Security Contexts** - Running as non-root  
✅ **Init Containers** - Dependency management  
✅ **Labels & Selectors** - Resource organization

---

## 📝 Portfolio/Resume Talking Points

**You can say:**

> "I containerized a full-stack e-commerce application and deployed it to Kubernetes using Minikube for local development. The architecture includes:
>
> - **StatefulSet** for PostgreSQL with persistent volume claims
> - **Deployments** for stateless backend (Flask) and frontend (React/Nginx) services  
> - **ConfigMaps** and **Secrets** for configuration management
> - **Horizontal Pod Autoscaling** based on CPU/memory metrics
> - **Pod Disruption Budgets** for high availability
> - **Health probes** (liveness, readiness, startup) for all services
> - **Resource requests and limits** for efficient cluster utilization
> - **Ingress** configuration for production-ready HTTP routing
>
> I can demonstrate scaling, self-healing, rolling updates, and rollbacks. The application is also deployable to cloud platforms like GKE, EKS, or AKS with minimal changes."

---

## 🚀 One-Line Deploy Script

Save this as `quick-k8s.sh`:

```bash
#!/bin/bash
minikube start --driver=docker --cpus=4 --memory=4096 && \
minikube addons enable metrics-server && \
eval $(minikube docker-env) && \
cd "/mnt/c/New Volume (D)/repo/DevOps with AI Antigravity" && \
docker build -t ecommerce-backend:v1 ./backend && \
docker build -t ecommerce-frontend:v1 ./frontend && \
cd k8s && \
sed 's|image: your-registry/ecommerce-backend:v1|image: ecommerce-backend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g' 04-backend-deployment.yaml > 04-backend-deployment-local.yaml && \
sed 's|image: your-registry/ecommerce-frontend:v1|image: ecommerce-frontend:v1|g; s|imagePullPolicy: Always|imagePullPolicy: Never|g; s|type: LoadBalancer|type: NodePort|g' 05-frontend-deployment.yaml > 05-frontend-deployment-local.yaml && \
kubectl apply -f 01-namespace-config-secrets.yaml && \
kubectl apply -f 02-postgres-statefulset.yaml && \
sleep 10 && \
kubectl apply -f 03-redis-deployment.yaml && \
kubectl apply -f 04-backend-deployment-local.yaml && \
kubectl apply -f 05-frontend-deployment-local.yaml && \
echo "Deployment complete! Access with: minikube service frontend -n ecommerce"
```

**Run it:**
```bash
chmod +x quick-k8s.sh
./quick-k8s.sh
```

---

## 📸 Screenshots for Portfolio

Take these screenshots to showcase:

1. **`kubectl get all -n ecommerce`** - Shows all your resources
2. **`kubectl get pods -n ecommerce`** - Shows running pods
3. **`minikube dashboard`** - Visual cluster overview
4. **Browser with app running** - Proof it works
5. **`kubectl top pods -n ecommerce`** - Resource monitoring
6. **`kubectl describe hpa -n ecommerce`** - Autoscaling config

---

## 🎓 Interview Questions You Can Answer

**Q: "Why did you use a StatefulSet for PostgreSQL?"**  
A: "StatefulSets provide stable pod identities and persistent storage, which databases need. Each pod gets a dedicated PVC that persists even if the pod is recreated."

**Q: "How does your application handle pod failures?"**  
A: "Kubernetes automatically restarts failed pods. I've configured health probes to detect failures early, and Pod Disruption Budgets ensure minimum availability during maintenance."

**Q: "How would you deploy this to production?"**  
A: "I'd push images to a container registry (ECR/GCR/ACR), update image references, configure proper secrets management (AWS Secrets Manager/Vault), set up Ingress with SSL, implement network policies, and deploy to a managed Kubernetes service like EKS/GKE/AKS."

---

## ⚡ Cleanup

When done demonstrating:

```bash
# Delete application
kubectl delete namespace ecommerce

# Stop Minikube
minikube stop

# Or delete completely
minikube delete
```

---

**You're now ready to showcase enterprise-level Kubernetes skills!** 🚀

Run the quick-start commands and you'll have a production-like K8s deployment in under 10 minutes.
