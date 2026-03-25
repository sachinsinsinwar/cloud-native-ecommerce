# 🚀 Cloud-Native E-Commerce: Resume & Learning Guide

This document is your master reference for understanding exactly what you built, why you built it, and how to confidently talk about it in technical interviews.

---

## Part 1: What to Add to Your Resume

Add this project to your **Experience** or **Projects** section. Modify the bullet points to fit the length of your resume.

**Cloud-Native E-Commerce Platform (DevSecOps / SRE)**
*Live Website: https://ecommerce.sachininfo.xyz | API: https://ecommerceapi.sachininfo.xyz*
* **Architecture & Containerization**: Architected a highly scalable full-stack application (React, Flask, PostgreSQL, Redis) by containerizing services using multi-stage Docker builds, reducing image sizes and deployment times.
* **Kubernetes Orchestration**: Deployed the microservices architecture onto a live AWS LightSail K3s Kubernetes cluster, utilizing Deployments, StatefulSets (for persistent database storage), and Services for robust self-healing and zero-downtime rolling updates.
* **CI/CD Automation**: Engineered a continuous integration and continuous deployment (CI/CD) pipeline using GitHub Actions to autonomously build, tag, and push immutable Docker images to Docker Hub upon code merges.
* **Traffic Routing & Security**: Configured an NGINX Ingress Controller paired with Cloudflare DNS proxying to route external traffic. Automated zero-trust SSL/TLS certificate provisioning using Cert-Manager and Let's Encrypt via HTTP-01 ACME challenges.
* **Observability & Logging**: Implemented a comprehensive monitoring stack using Prometheus for metrics collection, Loki for log aggregation, and Grafana for real-time visualization of cluster health, CPU/RAM limits, and pod stability.

**Skills to add to your "Technical Skills" section:**
`Kubernetes (K3s/K8s)` | `Docker / Docker Compose` | `GitHub Actions (CI/CD)` | `AWS (LightSail)` | `Nginx Ingress` | `Prometheus & Grafana` | `Let's Encrypt / Cert-Manager` | `Cloudflare DNS` | `Linux / Bash`

---

## Part 2: Complete Learning Overview (What, Why, How)

If an interviewer asks you about this project, this is how you explain every single piece of the puzzle.

### 1. Docker & Containerization
* **What**: We packaged the React frontend and Flask backend into isolated "Containers" using `Dockerfile`s.
* **Why**: "It works on my machine" is the biggest problem in software. By containerizing, we guarantee that the exact same environment (Node.js versions, Python libraries) runs identically on your local laptop, the GitHub testing server, and the production AWS server.
* **How**: We used **Multi-Stage Builds**. For the frontend, Stage 1 installed Node.js and built the React code into static HTML/JS files. Stage 2 threw away the heavy Node.js environment and only placed the lightweight static files into an ultra-fast NGINX web server image.

### 2. Kubernetes (K3s) on AWS
* **What**: Kubernetes (K8s) is an orchestration engine. K3s is a lightweight, production-grade version of Kubernetes optimized for smaller servers.
* **Why**: If a Docker container crashes, it stays dead. Kubernetes actively monitors the containers (Pods). If the backend crashes due to a bug, K8s restarts it instantly (Self-Healing). If traffic spikes, K8s can spin up more replicas (Auto-Scaling).
* **How**: 
  - **Deployments**: We wrapped the stateless Frontend and Backend in `Deployment` YAMLs, telling Kubernetes exactly how much CPU to reserve and how many replicas to run.
  - **StatefulSets**: Databases (PostgreSQL) cannot be freely destroyed and recreated anywhere, otherwise data is lost. We used a `StatefulSet` with a `PersistentVolumeClaim` (PVC) utilizing the `local-path` storage class to ensure the database data survives server reboots.

### 3. CI/CD (GitHub Actions)
* **What**: Continuous Integration & Continuous Deployment.
* **Why**: Manually logging into a server, pulling code, building Docker images, and restarting servers takes 20 minutes and is prone to human error. CI/CD makes it autonomous.
* **How**: We wrote a `.github/workflows/docker-publish.yml` script. Every time you run `git push origin staging`, GitHub spins up a temporary virtual machine, checks out your code, safely injects the API URL using `build-args`, builds the Docker images, and pushes them to Docker Hub.

### 4. NGINX Ingress Controller
* **What**: The traffic cop at the front door of your Kubernetes cluster.
* **Why**: Pods have internal IP addresses that the outside internet cannot access. We need a secure front door that listens on Ports 80 and 443 and directs users to the correct internal container based on the URL they typed.
* **How**: We created an `Ingress` YAML. We wrote rules saying: "If someone asks for `ecommerce.sachininfo.xyz`, send them to the internal `frontend` Service on port 80. If they ask for `ecommerceapi`, send them to the `backend` Service on port 5000."

### 5. SSL & Security (Cert-Manager + Cloudflare)
* **What**: Cert-Manager is an automated security agent living inside Kubernetes. Cloudflare is a DNS proxy.
* **Why**: Serving HTTP is wildly insecure. We need HTTPS (the padlock next to the URL). Buying and rotating SSL certificates manually is tedious.
* **How**: 
  - Cloudflare was set to "DNS Only" initially to point the URLs directly to your AWS IP.
  - We applied `cert-manager.io/cluster-issuer: letsencrypt-prod` to our Ingress.
  - Cert-Manager saw this, reached out to Let's Encrypt (a free certificate authority), and initiated an "HTTP-01 Challenge". Let's Encrypt essentially said: "Prove you own this domain by serving a specific secret file."
  - Cert-Manager dynamically created a temporary `cm-acme-http-solver` pod to serve that file. Once Let's Encrypt read it, the challenge passed, the certificate was issued as a Kubernetes `Secret`, and the solver pod was deleted. Your site became HTTPS forever.

### 6. Observability (Prometheus, Grafana, Loki)
* **What**: The sensory nervous system of your cluster.
* **Why**: If the website goes down at 3 AM, you need to know *why*. Did it run out of RAM? Did the database crash? You can't guess; you need metrics.
* **How**: 
  - **Prometheus** continuously scrapes numeric metrics (CPU usage, memory limits) from every node and pod.
  - **Loki** and **Promtail** continuously scrape the live text terminal logs from every pod.
  - **Grafana** is the visualization dashboard that takes the raw data from Prometheus and Loki and turns it into beautiful, readable charts. You access it securely via `grafana.sachininfo.xyz`.
