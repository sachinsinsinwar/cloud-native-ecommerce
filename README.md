# cloud-native-ecommerce

A full-stack e-commerce platform deployed on AWS using Kubernetes, with automated CI/CD, SSL, and a full observability stack.

The web application (React frontend + Flask backend) was built with AI assistance. The focus of this project is the cloud infrastructure, containerization, and DevOps pipeline.

---

## Live URLs

- Frontend: https://ecommerce.sachininfo.xyz
- Backend API: https://ecommerceapi.sachininfo.xyz/health
- Grafana: https://grafana.sachininfo.xyz

---

## Stack

- Frontend: React 18 + Vite, served via Nginx
- Backend: Flask (Python), JWT auth, REST API
- Database: PostgreSQL with persistent volume claims
- Cache: Redis for sessions and product caching
- Containers: Docker + Docker Compose
- Orchestration: K3s (Kubernetes) on AWS Lightsail
- Ingress: Nginx Ingress Controller
- SSL: Cert-Manager + Let's Encrypt (automated HTTP-01 challenge)
- DNS and Security: Cloudflare WAF, HSTS, TLS 1.2+, Bot Fight Mode
- CI/CD: GitHub Actions -> Docker Hub -> K3s
- Monitoring: Prometheus, Loki, Promtail, Grafana

---

## How the pipeline works

Every git push to the staging branch triggers GitHub Actions, which builds Docker images, pushes them to Docker Hub, and deploys to the K3s cluster. Cert-Manager automatically provisions and renews SSL certificates from Let's Encrypt. Cloudflare proxies all traffic with WAF and DDoS protection in front.

---

## Local setup
```bash
git clone https://github.com/sachinsinsinwar/cloud-native-ecommerce
cd cloud-native-ecommerce
docker-compose up --build
```

Frontend runs on http://localhost:3000
Backend runs on http://localhost:5000

---

## Project structure
```
.github/workflows/    CI/CD pipeline
backend/              Flask API (routes, models, JWT, Redis cache)
frontend/             React app (components, auth context, API client)
database/             PostgreSQL init and seed scripts
k8s/                  Kubernetes manifests
docker-compose.yml    Local development
```

---

## What I built vs what was AI-assisted

Infrastructure, Kubernetes manifests, CI/CD pipeline, Cloudflare configuration, SSL setup, Nginx Ingress, and the observability stack (Prometheus, Loki, Grafana) — all done manually.

The React frontend and Flask backend application code was built with AI assistance (vibe coding). This let me focus on the DevOps and cloud infrastructure side, which is the core of this project.

---

Built by Sachin Singh
