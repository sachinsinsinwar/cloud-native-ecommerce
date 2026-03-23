# Ingress Controller and TLS Setup Guide

## 📚 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What is Ingress?

An **Ingress** is a Kubernetes resource that manages external HTTP/HTTPS access to services in a cluster. It provides:

- **Load balancing** - Distribute traffic across pods
- **SSL/TLS termination** - Handle HTTPS at the edge
- **Name-based virtual hosting** - Route based on domain names
- **Path-based routing** - Route based on URL paths

### Why Use Ingress?

**Without Ingress:**
```
User → LoadBalancer 1 → Frontend Service
User → LoadBalancer 2 → Backend Service
User → LoadBalancer 3 → API Service
```
- **Problem:** Multiple LoadBalancers = High cost
- **Problem:** Manual SSL certificate management per service

**With Ingress:**
```
User → Single LoadBalancer → Ingress Controller → {Frontend, Backend, API}
```
- **Benefits:** Single entry point, centralized SSL, cost-effective
- **Benefits:** Advanced routing, rate limiting, authentication

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                         INTERNET                             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS (443)
                         ▼
              ┌──────────────────────┐
              │   Load Balancer      │ (Cloud Provider)
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Ingress Controller   │ (NGINX Pod)
              │  - SSL Termination   │
              │  - Routing Logic     │
              │  - Load Balancing    │
              └──────────┬───────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  ┌─────────┐      ┌─────────┐     ┌─────────┐
  │Frontend │      │Backend  │     │  API    │
  │Service  │      │Service  │     │ Service │
  └────┬────┘      └────┬────┘     └────┬────┘
       │                │                │
  ┌────┴────┐      ┌────┴────┐     ┌────┴────┐
  │ Pods    │      │ Pods    │     │ Pods    │
  └─────────┘      └─────────┘     └─────────┘
```

### Flow

1. **User Request** → `https://yourdomain.com/products`
2. **DNS Resolution** → Resolves to LoadBalancer IP
3. **LoadBalancer** → Routes to Ingress Controller pod
4. **Ingress Controller**:
   - Terminates SSL/TLS
   - Checks routing rules in Ingress resource
   - Routes to appropriate service (frontend/backend)
5. **Service** → Load balances to backend pods
6. **Pod** → Processes request and returns response

---

## Installation

### Prerequisites

```bash
# Verify cluster is running
kubectl cluster-info

# Check nodes
kubectl get nodes
```

### Option 1: Minikube (Local Development)

Minikube has a built-in Ingress addon:

```bash
# Enable Ingress addon
minikube addons enable ingress

# Verify installation
kubectl get pods -n ingress-nginx

# Expected output:
# NAME                                        READY   STATUS
# ingress-nginx-controller-xxxx              1/1     Running
```

### Option 2: Production (Helm - Recommended)

For production clusters (GKE, EKS, AKS):

```bash
# Add Helm repository
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress Controller
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.metrics.enabled=true

# Verify
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx

# Get LoadBalancer IP (may take a few minutes)
kubectl get svc ingress-nginx-controller -n ingress-nginx
```

### Option 3: Production (kubectl)

```bash
# Apply official manifest
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Verify
kubectl get pods -n ingress-nginx
kubectl get svc -n ingress-nginx
```

---

## Configuration

### cert-manager Installation

cert-manager automates SSL certificate management with Let's Encrypt:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Verify installation
kubectl get pods -n cert-manager

# Expected output:
# NAME                                       READY   STATUS
# cert-manager-xxxx                         1/1     Running
# cert-manager-cainjector-xxxx              1/1     Running
# cert-manager-webhook-xxxx                 1/1     Running
```

### ClusterIssuer Configuration

**For Production:**

Edit `07-cert-manager.yaml` and update email:

```yaml
spec:
  acme:
    email: your-email@example.com  # ← Change this!
```

Apply:

```bash
# Apply ClusterIssuer
kubectl apply -f k8s/07-cert-manager.yaml

# Verify
kubectl get clusterissuer

# Expected output:
# NAME                  READY   AGE
# letsencrypt-prod      True    10s
# letsencrypt-staging   True    10s
# selfsigned-issuer     True    10s
```

### Ingress Resource Configuration

**For Production:**

Edit `08-ingress-production.yaml` and update domains:

```yaml
tls:
- hosts:
  - yourdomain.com        # ← Change to your domain
  - www.yourdomain.com    # ← Change to your domain
  - api.yourdomain.com    # ← Change to your domain
```

**For Local (Minikube):**

Use `09-ingress-local.yaml` - no changes needed!

---

## Testing

### Local Testing (Minikube)

#### 1. Deploy Application

```bash
# Deploy all resources
cd k8s
kubectl apply -f 01-namespace-config-secrets.yaml
kubectl apply -f 02-postgres-statefulset.yaml
kubectl apply -f 03-redis-deployment.yaml
kubectl apply -f 04-backend-deployment.yaml
kubectl apply -f 05-frontend-deployment.yaml

# Wait for pods
kubectl get pods -n ecommerce -w
```

#### 2. Apply Ingress

```bash
# Apply local Ingress
kubectl apply -f 09-ingress-local.yaml

# Verify
kubectl get ingress -n ecommerce
```

#### 3. Configure Hosts File

Get Minikube IP:

```bash
minikube ip
# Example output: 192.168.49.2
```

**Windows:** Edit `C:\Windows\System32\drivers\etc\hosts` (as Administrator)  
**Linux/Mac:** Edit `/etc/hosts` (with sudo)

Add line:
```
192.168.49.2 ecommerce.local www.ecommerce.local api.ecommerce.local
```

#### 4. Access Application

**Frontend:**
```bash
# Browser
http://ecommerce.local

# Or curl
curl http://ecommerce.local
```

**Backend API:**
```bash
# Health check
curl http://api.ecommerce.local/health

# Get products
curl http://api.ecommerce.local/products
```

#### 5. Alternative: Path-Based Routing (No hosts file)

```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Frontend
curl http://$MINIKUBE_IP/

# Backend API
curl http://$MINIKUBE_IP/api/health
```

---

## Production Deployment

### Step 1: Configure DNS

Point your domains to the LoadBalancer IP:

```bash
# Get LoadBalancer external IP
kubectl get svc ingress-nginx-controller -n ingress-nginx

# Copy the EXTERNAL-IP value
```

Create DNS A records:

| Record Type | Name | Value |
|------------|------|-------|
| A | @ | `<EXTERNAL-IP>` |
| A | www | `<EXTERNAL-IP>` |
| A | api | `<EXTERNAL-IP>` |

Or use CNAME for subdomains:

| Record Type | Name | Value |
|------------|------|-------|
| A | @ | `<EXTERNAL-IP>` |
| CNAME | www | `yourdomain.com` |
| CNAME | api | `yourdomain.com` |

### Step 2: Update Ingress Configuration

Edit `08-ingress-production.yaml`:

```yaml
# Update email in ClusterIssuer
spec:
  acme:
    email: admin@yourdomain.com

# Update domains in Ingress
tls:
- hosts:
  - yourdomain.com
  - www.yourdomain.com
  - api.yourdomain.com

# Update CORS origins
nginx.ingress.kubernetes.io/cors-allow-origin: "https://yourdomain.com,https://www.yourdomain.com"
```

### Step 3: Deploy cert-manager

```bash
# Apply ClusterIssuer
kubectl apply -f k8s/07-cert-manager.yaml

# Verify
kubectl get clusterissuer
```

### Step 4: Deploy Ingress

**Important:** Test with staging first to avoid rate limits!

```bash
# Edit ingress to use staging
# Change: cert-manager.io/cluster-issuer: "letsencrypt-staging"
kubectl apply -f k8s/08-ingress-production.yaml

# Wait for certificate (1-2 minutes)
kubectl get certificate -n ecommerce -w

# Check certificate status
kubectl describe certificate ecommerce-tls-secret -n ecommerce
```

### Step 5: Verify Certificate

```bash
# Check cert-manager logs
kubectl logs -n cert-manager -l app=cert-manager

# View certificate details
kubectl get secret ecommerce-tls-secret -n ecommerce -o yaml
```

### Step 6: Switch to Production

Once staging works:

```bash
# Edit ingress
# Change: cert-manager.io/cluster-issuer: "letsencrypt-prod"

# Delete old certificate
kubectl delete secret ecommerce-tls-secret -n ecommerce
kubectl delete certificate ecommerce-tls -n ecommerce

# Reapply
kubectl apply -f k8s/08-ingress-production.yaml

# Wait for new certificate
kubectl get certificate -n ecommerce -w
```

### Step 7: Test HTTPS

```bash
# Browser
https://yourdomain.com
https://www.yourdomain.com
https://api.yourdomain.com/health

# curl with certificate validation
curl -v https://yourdomain.com
```

---

## Troubleshooting

### Certificate Not Issued

**Check certificate status:**
```bash
kubectl describe certificate ecommerce-tls -n ecommerce
```

**Check challenges:**
```bash
kubectl get challenge -n ecommerce
kubectl describe challenge <challenge-name> -n ecommerce
```

**Check cert-manager logs:**
```bash
kubectl logs -n cert-manager -l app=cert-manager -f
```

**Common issues:**
- DNS not pointing to LoadBalancer IP
- Firewall blocking port 80/443
- Rate limit exceeded (use staging)
- Wrong email in ClusterIssuer

### Ingress Not Working

**Check Ingress status:**
```bash
kubectl get ingress -n ecommerce
kubectl describe ingress ecommerce-ingress -n ecommerce
```

**Check Ingress controller logs:**
```bash
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller -f
```

**Verify backend service:**
```bash
kubectl get svc -n ecommerce
kubectl get endpoints -n ecommerce
```

**Test backend directly:**
```bash
kubectl port-forward svc/backend 5000:5000 -n ecommerce
curl http://localhost:5000/health
```

### SSL/TLS Issues

**Check secret exists:**
```bash
kubectl get secret ecommerce-tls-secret -n ecommerce
```

**View certificate details:**
```bash
kubectl get secret ecommerce-tls-secret -n ecommerce -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout
```

**Force renewal:**
```bash
kubectl delete secret ecommerce-tls-secret -n ecommerce
# cert-manager will recreate it automatically
```

### 404 Errors

**Check path matching:**
```bash
# View Ingress rules
kubectl get ingress ecommerce-ingress -n ecommerce -o yaml

# Test specific paths
curl -v http://yourdomain.com/
curl -v http://api.yourdomain.com/health
```

**Verify rewrite rules:**
```bash
# Check annotations
kubectl describe ingress ecommerce-ingress -n ecommerce | grep -A 10 Annotations
```

---

## Key Concepts Explained

### Security Headers

**X-Frame-Options**: Prevents clickjacking attacks
**X-Content-Type-Options**: Prevents MIME sniffing
**X-XSS-Protection**: Enables browser XSS filter
**HSTS**: Forces HTTPS for 1 year

### Rate Limiting

Protects against:
- DDoS attacks
- Brute force attempts
- API abuse

```yaml
nginx.ingress.kubernetes.io/limit-rps: "100"  # 100 requests/sec per IP
nginx.ingress.kubernetes.io/limit-connections: "10"  # 10 concurrent connections per IP
```

### CORS Configuration

Allows frontend (different domain) to call backend API:

```yaml
nginx.ingress.kubernetes.io/enable-cors: "true"
nginx.ingress.kubernetes.io/cors-allow-origin: "https://yourdomain.com"
nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
```

### Path Types

**Exact**: Matches exact path only
```yaml
path: /api/v1/health
pathType: Exact
# Matches: /api/v1/health
# Doesn't match: /api/v1/health/
```

**Prefix**: Matches path prefix
```yaml
path: /api
pathType: Prefix
# Matches: /api, /api/, /api/products, /api/users/123
```

---

## Production Checklist

Before going live:

- [ ] DNS configured and propagated
- [ ] Let's Encrypt email updated
- [ ] Tested with staging issuer first
- [ ] Production certificate issued
- [ ] HTTPS working for all domains
- [ ] HTTP → HTTPS redirect working
- [ ] Security headers in place
- [ ] CORS configured correctly
- [ ] Rate limiting tested
- [ ] SSL certificate auto-renewal verified
- [ ] Monitoring/alerting configured
- [ ] Backup Ingress configuration

---

## Summary

**You now have:**

✅ **NGINX Ingress Controller** - Entry point for all traffic  
✅ **cert-manager** - Automatic SSL certificate management  
✅ **Let's Encrypt Integration** - Free SSL certificates  
✅ **Security Headers** - Protection against common attacks  
✅ **CORS Configuration** - Secure cross-origin requests  
✅ **Rate Limiting** - DDoS protection  
✅ **Production-ready configuration** - Best practices implemented

**Files created:**
- `06-ingress-controller.yaml` - Controller installation guide
- `07-cert-manager.yaml` - ClusterIssuers for SSL
- `08-ingress-production.yaml` - Production Ingress with all features
- `09-ingress-local.yaml` - Simplified local testing
- `INGRESS-GUIDE.md` - This comprehensive guide

**Access your application:**
- **Local:** `http://ecommerce.local`
- **Production:** `https://yourdomain.com`
