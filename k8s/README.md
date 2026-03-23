# Kubernetes Deployment Guide for E-Commerce Application

## 📋 Overview

This directory contains Kubernetes manifests for deploying the e-commerce application to a Kubernetes cluster. The manifests follow production-ready best practices and include:

- ✅ Namespace isolation
- ✅ ConfigMaps for configuration
- ✅ Secrets for sensitive data
- ✅ StatefulSet for PostgreSQL with persistent storage
- ✅ Deployments for stateless services
- ✅ Services for network access
- ✅ Horizontal Pod Autoscaling (HPA)
- ✅ Pod Disruption Budgets (PDB)
- ✅ Ingress for external access
- ✅ Health probes (liveness, readiness, startup)
- ✅ Resource limits and requests
- ✅ Security contexts

---

## 📁 Manifest Files

| File | Description |
|------|-------------|
| `01-namespace-config-secrets.yaml` | Namespace, ConfigMaps, and Secrets |
| `02-postgres-statefulset.yaml` | PostgreSQL StatefulSet with PVC |
| `03-redis-deployment.yaml` | Redis Deployment for caching |
| `04-backend-deployment.yaml` | Flask backend Deployment + HPA + PDB |
| `05-frontend-deployment.yaml` | React frontend Deployment + Ingress |

---

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes Cluster** (v1.20+)
   - Local: Minikube, Kind, Docker Desktop
   - Cloud: GKE, EKS, AKS

2. **kubectl** installed and configured

3. **Container Images** built and pushed to registry
   ```bash
   # Build and push backend
   docker build -t your-registry/ecommerce-backend:v1 ./backend
   docker push your-registry/ecommerce-backend:v1
   
   # Build and push frontend
   docker build -t your-registry/ecommerce-frontend:v1 ./frontend
   docker push your-registry/ecommerce-frontend:v1
   ```

4. **Update image references** in deployment files:
   - `04-backend-deployment.yaml`: Line ~73
   - `05-frontend-deployment.yaml`: Line ~64

### Deploy to Kubernetes

```bash
# Navigate to k8s directory
cd k8s

# Apply manifests in order
kubectl apply -f 01-namespace-config-secrets.yaml
kubectl apply -f 02-postgres-statefulset.yaml
kubectl apply -f 03-redis-deployment.yaml
kubectl apply -f 04-backend-deployment.yaml
kubectl apply -f 05-frontend-deployment.yaml

# Or apply all at once
kubectl apply -f .
```

### Verify Deployment

```bash
# Check all resources in namespace
kubectl get all -n ecommerce

# Check pod status
kubectl get pods -n ecommerce

# Check services
kubectl get svc -n ecommerce

# Check persistent volumes
kubectl get pvc -n ecommerce

# View pod logs
kubectl logs -n ecommerce -l app=backend --tail=50
kubectl logs -n ecommerce -l app=frontend --tail=50
```

---

## 🔐 Security Configuration

### Update Secrets (CRITICAL!)

The provided secrets use example base64-encoded values. **You MUST change these in production!**

```bash
# Generate strong passwords
POSTGRES_PASS=$(openssl rand -base64 32)
REDIS_PASS=$(openssl rand -base64 32)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Base64 encode them
echo -n "$POSTGRES_PASS" | base64
echo -n "$REDIS_PASS" | base64
echo -n "$SECRET_KEY" | base64

# Update the values in 01-namespace-config-secrets.yaml
```

### Best Practices for Production

1. **Use External Secret Management**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Google Secret Manager
   - Azure Key Vault

2. **Enable RBAC**
   - Create service accounts with minimal permissions
   - Use Pod Security Policies/Standards

3. **Network Policies**
   - Restrict pod-to-pod communication
   - Only allow necessary traffic

4. **Image Security**
   - Use specific image tags (not `latest`)
   - Scan images for vulnerabilities
   - Use private container registry

---

## 📊 Monitoring and Observability

### Metrics Server (Required for HPA)

```bash
# Install metrics-server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Verify
kubectl top nodes
kubectl top pods -n ecommerce
```

### Prometheus + Grafana (Recommended)

```bash
# Install using Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

### Logging (Recommended)

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Loki + Grafana**
- **Cloud provider logging** (CloudWatch, Stackdriver, Azure Monitor)

---

## 🔧 Configuration Updates

### Update ConfigMap

```bash
# Edit the configmap
kubectl edit configmap ecommerce-config -n ecommerce

# Or update the file and reapply
kubectl apply -f 01-namespace-config-secrets.yaml

# Restart pods to pick up changes
kubectl rollout restart deployment/backend -n ecommerce
kubectl rollout restart deployment/frontend -n ecommerce
```

### Update Secrets

```bash
# Create new secret value
NEW_SECRET=$(echo -n "new-password" | base64)

# Update secret
kubectl patch secret ecommerce-secrets -n ecommerce \
  -p '{"data":{"SECRET_KEY":"'$NEW_SECRET'"}}'

# Restart pods
kubectl rollout restart deployment/backend -n ecommerce
```

---

## 🌐 Accessing the Application

### Using LoadBalancer (Cloud Providers)

```bash
# Get external IP
kubectl get svc frontend -n ecommerce

# Access application
# http://<EXTERNAL-IP>
```

### Using Ingress (Recommended)

1. **Install Ingress Controller**
   ```bash
   # Nginx Ingress
   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
   ```

2. **Configure DNS**
   - Point your domain to the Ingress LoadBalancer IP
   - Update hosts in `05-frontend-deployment.yaml` Ingress

3. **Setup SSL/TLS**
   ```bash
   # Install cert-manager
   kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
   ```

### Local Testing (NodePort)

```bash
# Change service type to NodePort in manifests
# Or patch existing service
kubectl patch svc frontend -n ecommerce -p '{"spec":{"type":"NodePort"}}'

# Get NodePort
kubectl get svc frontend -n ecommerce

# Access on http://localhost:<NodePort>
```

### Port Forwarding (Development)

```bash
# Forward backend
kubectl port-forward svc/backend 5000:5000 -n ecommerce

# Forward frontend
kubectl port-forward svc/frontend 3000:80 -n ecommerce

# Access:
# Frontend: http://localhost:3000
# Backend: http://localhost:5000
```

---

## 🔄 Rolling Updates

### Update Backend

```bash
# Build new image
docker build -t your-registry/ecommerce-backend:v2 ./backend
docker push your-registry/ecommerce-backend:v2

# Update deployment
kubectl set image deployment/backend backend=your-registry/ecommerce-backend:v2 -n ecommerce

# Monitor rollout
kubectl rollout status deployment/backend -n ecommerce

# Rollback if needed
kubectl rollout undo deployment/backend -n ecommerce
```

### Update Frontend

```bash
# Build new image
docker build -t your-registry/ecommerce-frontend:v2 ./frontend
docker push your-registry/ecommerce-frontend:v2

# Update deployment
kubectl set image deployment/frontend frontend=your-registry/ecommerce-frontend:v2 -n ecommerce

# Monitor
kubectl rollout status deployment/frontend -n ecommerce
```

---

## 📈 Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n ecommerce

# Scale frontend
kubectl scale deployment frontend --replicas=5 -n ecommerce
```

### Auto-scaling (HPA)

```bash
# View HPA status
kubectl get hpa -n ecommerce

# Describe HPA
kubectl describe hpa backend-hpa -n ecommerce

# Edit HPA parameters
kubectl edit hpa backend-hpa -n ecommerce
```

---

## 🗄️ Database Management

### Access PostgreSQL

```bash
# Get pod name
kubectl get pods -n ecommerce -l app=postgres

# Connect to PostgreSQL
kubectl exec -it postgres-0 -n ecommerce -- psql -U postgres -d ecommerce_db

# Run SQL commands
\dt  # List tables
\d users  # Describe users table
SELECT * FROM products LIMIT 5;
```

### Backup Database

```bash
# Manual backup
kubectl exec postgres-0 -n ecommerce -- pg_dump -U postgres ecommerce_db > backup.sql

# Restore from backup
kubectl exec -i postgres-0 -n ecommerce -- psql -U postgres ecommerce_db < backup.sql
```

### Database Migrations

For production, use database migration tools:
- **Alembic** (Python/Flask)
- **Flyway**
- **Liquibase**

---

## 🐛 Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -n ecommerce

# Describe pod for events
kubectl describe pod <pod-name> -n ecommerce

# Check logs
kubectl logs <pod-name> -n ecommerce
kubectl logs <pod-name> -n ecommerce --previous  # Previous container logs
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n ecommerce

# Check if pods are ready
kubectl get pods -n ecommerce -o wide

# Test service connectivity from another pod
kubectl run -it --rm debug --image=busybox --restart=Never -n ecommerce -- sh
# wget -O- http://backend:5000/health
```

### Database Connection Issues

```bash
# Check if postgres is running
kubectl get statefulset postgres -n ecommerce

# Check postgres logs
kubectl logs postgres-0 -n ecommerce

# Verify database URL in backend
kubectl exec -it <backend-pod> -n ecommerce -- env | grep DATABASE_URL
```

### Resource Issues

```bash
# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n ecommerce

# Describe nodes for resource pressure
kubectl describe nodes
```

---

## 🧹 Cleanup

### Delete All Resources

```bash
# Delete namespace (removes everything)
kubectl delete namespace ecommerce

# Or delete individual resources
kubectl delete -f k8s/
```

### Delete Persistent Volumes

```bash
# List PVCs
kubectl get pvc -n ecommerce

# Delete PVC
kubectl delete pvc postgres-data-postgres-0 -n ecommerce

# Note: This will delete all database data!
```

---

## 📚 Architecture Decisions Explained

### Why StatefulSet for PostgreSQL?

✅ **Stable pod identity** (postgres-0, postgres-1, etc.)
✅ **Persistent storage** per pod (data survives pod restarts)
✅ **Ordered deployment** (pods created/deleted in sequence)
✅ **Stable network identity** (DNS name stays constant)

### Why Deployment for Backend/Frontend?

✅ **Stateless** (no data stored in pods)
✅ **Easy scaling** (add/remove replicas freely)
✅ **Rolling updates** (zero-downtime deployments)
✅ **Self-healing** (automatic restart on failure)

### Why ConfigMaps and Secrets?

✅ **Separation of config from code**
✅ **Easy updates** without rebuilding images
✅ **Environment-specific configuration**
✅ **Security** (secrets encrypted at rest)

### Why HPA (Horizontal Pod Autoscaler)?

✅ **Automatic scaling** based on CPU/memory
✅ **Cost optimization** (scale down when idle)
✅ **Handle traffic spikes** automatically
✅ **Improved reliability**

### Why PDB (Pod Disruption Budget)?

✅ **High availability** during maintenance
✅ **Controlled disruptions** (node upgrades, etc.)
✅ **Prevents downtime** from voluntary disruptions

### Why Ingress?

✅ **Single entry point** for multiple services
✅ **SSL/TLS termination** at load balancer
✅ **Path/host-based routing**
✅ **Cost-effective** (1 load balancer vs many)

---

##  Production Checklist

Before deploying to production:

- [ ] Update all secrets with strong passwords
- [ ] Use private container registry
- [ ] Configure domain names and SSL certificates
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Set up logging (ELK/Loki)
- [ ] Configure backup strategy for database
- [ ] Set up CI/CD pipeline
- [ ] Configure resource quotas
- [ ] Enable network policies
- [ ] Set up alerting
- [ ] Document runbooks
- [ ] Test disaster recovery procedures
- [ ] Configure auto-scaling parameters
- [ ] Review security policies
- [ ] Set up cost monitoring

---

## 📖 Further Reading

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Production Best Practices](https://kubernetes.io/docs/setup/best-practices/)
- [Helm Charts](https://helm.sh/) - Package manager for Kubernetes
- [Kustomize](https://kustomize.io/) - Configuration management

---

**Your application is ready for Kubernetes deployment!** 🚀
