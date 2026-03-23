# Kubernetes Monitoring and Observability Guide

## 📚 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)  
- [Installation](#installation)
- [Configuration](#configuration)
- [Dashboards](#dashboards)
- [Alerts](#alerts)
- [Querying](#querying)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What is Observability?

**Observability** is the ability to understand the internal state of your system by examining its outputs. For Kubernetes applications, this includes:

**The Three Pillars:**
1. **Metrics** - Numerical data over time (CPU, memory, request rate)
2. **Logs** - Event records from applications and infrastructure
3. **Traces** - Request flow through distributed systems

### Monitoring Stack Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Prometheus** | Metrics collection and storage | 9090 |
| **AlertManager** | Alert routing and notifications | 9093 |
| **Grafana** | Visualization and dashboards | 3000 |
| **Loki** | Log aggregation | 3100 |
| **Promtail** | Log shipping (DaemonSet) | 9080 |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        OBSERVABILITY STACK                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  PROMETHEUS  │────────▶│ ALERTMANAGER │────────▶│  📧 Slack    │
│  (Metrics)   │         │  (Alerts)    │         │  📱 Email    │
└──────┬───────┘         └──────────────┘         │  📟 PagerDuty│
       │                                           └──────────────┘
       │ scrapes
       │
       ▼
┌──────────────────────────────────────────────────────────────────┐
│                      KUBERNETES CLUSTER                          │
│                                                                  │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  │
│  │Backend │  │Frontend│  │Postgres│  │ Redis  │  │Ingress │  │
│  │  Pods  │  │  Pods  │  │  Pod   │  │  Pod   │  │  Pod   │  │
│  │ :5000  │  │  :80   │  │  :5432 │  │  :6379 │  │  :80   │  │
│  └───┬────┘  └────────┘  └───┬────┘  └───┬────┘  └────────┘  │
│      │                        │           │                    │
│  /metrics              postgres-exporter  redis-exporter       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
       │                        │           │
       └────────────────────────┴───────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   GRAFANA    │
                 │ (Dashboards) │
                 └──────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                        LOG AGGREGATION                           │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│  │ Node 1   │  │ Node 2   │  │ Node 3   │                     │
│  │          │  │          │  │          │                     │
│  │Promtail  │  │Promtail  │  │Promtail  │                     │
│  │DaemonSet │  │DaemonSet │  │DaemonSet │                     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                     │
│       │             │             │                             │
│       └─────────────┴─────────────┘                             │
│                     │                                           │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │     LOKI     │                                   │
│              │  (Log Store) │                                   │
│              └──────┬───────┘                                   │
│                     │                                           │
│                     ▼                                           │
│              ┌──────────────┐                                   │
│              │   GRAFANA    │                                   │
│              │ (Log Viewer) │                                   │
│              └──────────────┘                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

```bash
# Ensure kubectl is configured
kubectl cluster-info

# Check available storage
kubectl get storageclass
```

### Quick Installation (Minikube)

```bash
# Navigate to k8s directory
cd k8s

# Create monitoring namespace and configs
kubectl apply -f 10-monitoring-namespace.yaml

# Deploy Prometheus and AlertManager
kubectl apply -f 11-prometheus.yaml

# Deploy Grafana
kubectl apply -f 12-grafana.yaml

# Deploy Loki and Promtail
kubectl apply -f 13-loki.yaml

# (Optional) Deploy exporters for PostgreSQL and Redis
kubectl apply -f 14-service-monitors.yaml

# Wait for all pods to be ready
kubectl get pods -n monitoring -w
```

### Verify Installation

```bash
# Check all monitoring components
kubectl get all -n monitoring

# Expected output:
# NAME                              READY   STATUS
# pod/prometheus-xxx                1/1     Running
# pod/alertmanager-xxx              1/1     Running
# pod/grafana-xxx                   1/1     Running
# pod/loki-xxx                      1/1     Running
# pod/promtail-xxx (on each node)   1/1     Running
```

---

## Configuration

### Access Monitoring UIs

**Minikube:**

```bash
# Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open: http://localhost:9090

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Open: http://localhost:3000
# Default login: admin/admin

# AlertManager
kubectl port-forward -n monitoring svc/alertmanager 9093:9093
# Open: http://localhost:9093
```

**Production (with Ingress):**

Grafana is already configured with Ingress at `grafana.local`.

Add to `/etc/hosts`:
```
<minikube-ip> grafana.local
```

Or update `12-grafana.yaml` with your domain:
```yaml
spec:
  rules:
    - host: grafana.yourdomain.com
```

### Grafana Initial Setup

1. **Login**  
   - URL: `http://localhost:3000`
   - Username: `admin`
   - Password: `admin` (change immediately!)

2. **Verify Data Sources**  
   - Navigate to: Configuration → Data Sources
   - Should see:
     - ✅ Prometheus (default)
     - ✅ Loki

3. **Create Your First Dashboard**  
   - Click "+" → Dashboard
   - Add Panel
   - Select Prometheus data source
   - Enter query (see [Querying](#querying) section)

---

## Dashboards

### Pre-Built Dashboards (Import)

Grafana has thousands of community dashboards. Here are recommended ones:

**Kubernetes Cluster:**
```
ID: 15757 - Kubernetes / Views / Global
ID: 15758 - Kubernetes / Views / Namespaces
ID: 15759 - Kubernetes / Views / Pods
```

**Nginx Ingress:**
```
ID: 9614 - Nginx Ingress Controller
```

**PostgreSQL:**
```
ID: 9628 - PostgreSQL Database
```

**Redis:**
```
ID: 11835 - Redis Dashboard
```

**How to Import:**
1. Go to Dashboards → Import
2. Enter dashboard ID
3. Select Prometheus data source
4. Click Import

### Custom Dashboard for E-Commerce App

Create a new dashboard with these panels:

**1. Request Rate**
```promql
sum(rate(http_requests_total{namespace="ecommerce"}[5m])) by (service)
```

**2. Error Rate**
```promql
sum(rate(http_requests_total{namespace="ecommerce",status=~"5.."}[5m]))
/
sum(rate(http_requests_total{namespace="ecommerce"}[5m]))
```

**3. Response Time (p95)**
```promql
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket{namespace="ecommerce"}[5m])) by (le, service)
)
```

**4. Active Pods**
```promql
count(kube_pod_status_phase{namespace="ecommerce",phase="Running"}) by (pod)
```

**5. CPU Usage**
```promql
sum(rate(container_cpu_usage_seconds_total{namespace="ecommerce"}[5m])) by (pod)
```

**6. Memory Usage**
```promql
sum(container_memory_usage_bytes{namespace="ecommerce"}) by (pod)
```

**7. Database Connections**
```promql
pg_stat_database_numbackends{datname="ecommerce_db"}
```

**8. Cache Hit Rate**
```promql
rate(redis_keyspace_hits_total[5m])
/
(rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m]))
```

---

## Alerts

### View Active Alerts

**Prometheus:**
```
http://localhost:9090/alerts
```

**AlertManager:**
```
http://localhost:9093/#/alerts
```

### Configure Alert Notifications

Edit `11-prometheus.yaml` AlertManager configuration:

**Email Notifications:**
```yaml
receivers:
  - name: 'critical'
    email_configs:
      - to: 'alerts@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp.gmail.com:587'
        auth_username: 'your-email@gmail.com'
        auth_password: 'your-app-password'
```

**Slack Notifications:**
```yaml
receivers:
  - name: 'critical'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        channel: '#alerts-critical'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

**After editing, apply changes:**
```bash
kubectl apply -f k8s/11-prometheus.yaml
kubectl rollout restart deployment/alertmanager -n monitoring
```

### Test Alerts

**Trigger a test alert:**
```bash
# Scale down backend to trigger PodDown alert
kubectl scale deployment backend --replicas=0 -n ecommerce

# Wait 2 minutes (alert for: 2m)
# Check AlertManager: http://localhost:9093

# Restore
kubectl scale deployment backend --replicas=3 -n ecommerce
```

---

## Querying

### PromQL (Prometheus Query Language)

**Basic Queries:**

```promql
# Current CPU usage for all pods
container_cpu_usage_seconds_total{namespace="ecommerce"}

# Request rate (last 5 minutes)
rate(http_requests_total[5m])

# Total requests by service
sum(http_requests_total) by (service)

# Memory usage in GB
container_memory_usage_bytes / 1024 / 1024 / 1024
```

**Advanced Queries:**

```promql
# 95th percentile response time
histogram_quantile(0.95,
  rate(http_request_duration_seconds_bucket[5m])
)

# Error rate percentage
100 * (
  sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
  sum(rate(http_requests_total[5m]))
)

# Pods using >80% memory
(container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.8

# Top 5 endpoints by request count
topk(5, sum(rate(http_requests_total[5m])) by (endpoint))
```

### LogQL (Loki Query Language)

**Basic Log Queries:**

```logql
# All logs from ecommerce namespace
{namespace="ecommerce"}

# Backend pod logs
{namespace="ecommerce", app="backend"}

# Error logs only
{namespace="ecommerce"} |= "error"

# Logs NOT containing "health"
{namespace="ecommerce"} != "health"
```

**Advanced Log Queries:**

```logql
# Count errors per minute
sum(rate({namespace="ecommerce"} |= "error" [1m])) by (pod)

# Parse JSON logs
{namespace="ecommerce"} | json | level="error"

# Regex pattern matching
{namespace="ecommerce"} |~ "status.*5[0-9]{2}"

# Top 10 error messages
topk(10, 
  sum by (error_message) (
    rate({namespace="ecommerce"} |= "error" [5m])
  )
)
```

---

## Troubleshooting

### Prometheus Not Scraping

**Check service discovery:**
```bash
# View targets in Prometheus
# http://localhost:9090/targets

# Check pod annotations
kubectl get pod <pod-name> -n ecommerce -o yaml | grep prometheus
```

**Expected annotations:**
```yaml
prometheus.io/scrape: "true"
prometheus.io/port: "5000"
prometheus.io/path: "/metrics"
```

**Add if missing:**
```bash
kubectl edit deployment backend -n ecommerce

# Add under spec.template.metadata.annotations:
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "5000"
```

### Grafana Can't Connect to Data Sources

**Check data source configuration:**
```bash
# Test from Grafana pod
kubectl exec -it deployment/grafana -n monitoring -- /bin/sh
wget -O- http://prometheus:9090/api/v1/labels
wget -O- http://loki:3100/ready
```

**Verify services:**
```bash
kubectl get svc -n monitoring
# Ensure prometheus and loki services exist
```

### Loki Not Receiving Logs

**Check Promtail pods:**
```bash
# Should be 1 per node
kubectl get pods -n monitoring -l app=promtail

# Check logs
kubectl logs -n monitoring -l app=promtail
```

**Check Loki ingestion:**
```bash
kubectl logs -n monitoring deployment/loki
```

**Common issues:**
- Promtail can't access `/var/log` - check DaemonSet volume mounts
- Loki storage full - check PVC size
- Label mismatch - verify Promtail config

### High Memory Usage

**Check resource limits:**
```bash
kubectl top pods -n monitoring
```

**Increase if needed:**
```yaml
# Edit deployment
kubectl edit deployment prometheus -n monitoring

# Increase limits:
resources:
  limits:
    memory: 4Gi
```

**Reduce retention:**
```yaml
args:
  - '--storage.tsdb.retention.time=15d'  # Default: 30d
```

---

## Important Metrics for E-Commerce

### Application Health

| Metric | Query | Threshold |
|--------|-------|-----------|
| **Request Rate** | `rate(http_requests_total[5m])` | Monitor trends |
| **Error Rate** | `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])` | < 1% |
| **Response Time (p95)** | `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))` | < 500ms |
| **Response Time (p99)** | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` | < 1s |

### Business Metrics

| Metric | Query | Importance |
|--------|-------|------------|
| **Orders/min** | `rate(orders_created_total[1m]) * 60` | Revenue indicator |
| **Cart Adds/min** | `rate(cart_additions_total[1m]) * 60` | User engagement |
| **Product Views** | `rate(product_views_total[5m])` | Traffic indicator |
| **Failed Orders** | `rate(orders_failed_total[5m])` | Revenue loss |

### Infrastructure

| Metric | Query | Alert When |
|--------|-------|------------|
| **Pod Restarts** | `rate(kube_pod_container_status_restarts_total[15m])` | > 0 |
| **CPU Usage** | `container_cpu_usage_seconds_total` | > 80% |
| **Memory Usage** | `container_memory_usage_bytes / container_spec_memory_limit_bytes` | > 90% |
| **Disk Usage** | `node_filesystem_avail_bytes / node_filesystem_size_bytes` | < 10% |

### Database (PostgreSQL)

| Metric | Query | Threshold |
|--------|-------|-----------|
| **Active Connections** | `pg_stat_database_numbackends` | < 90% max |
| **Query Duration** | `pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)` | > 95% |
| **Deadlocks** | `rate(pg_stat_database_deadlocks[5m])` | Alert on any |

### Cache (Redis)

| Metric | Query | Threshold |
|--------|-------|-----------|
| **Hit Rate** | `redis_keyspace_hits / (redis_keyspace_hits + redis_keyspace_misses)` | > 80% |
| **Memory Usage** | `redis_memory_used_bytes / redis_memory_max_bytes` | < 90% |
| **Evictions** | `rate(redis_evicted_keys_total[5m])` | Monitor trends |

---

## Production Checklist

Before going to production:

- [ ] Prometheus retention configured (storage size)
- [ ] Alert notifications configured (email/Slack/PagerDuty)
- [ ] Critical alerts tested and validated
- [ ] Grafana dashboards created for all services
- [ ] Admin password changed from default
- [ ] Persistent volumes configured (metrics/logs)
- [ ] Resource limits set appropriately
- [ ] Backup strategy for metrics/dashboards
- [ ] Metrics endpoints added to application code
- [ ] Database and cache exporters deployed
- [ ] Log retention policy configured
- [ ] On-call rotation configured in AlertManager
- [ ] Runbooks created for common alerts
- [ ] Monitoring stack itself is monitored

---

## Summary

**You now have:**

✅ **Prometheus** - Metrics collection from all services  
✅ **AlertManager** - Alert routing and notifications  
✅ **Grafana** - Beautiful dashboards and visualization  
✅ **Loki** - Centralized log aggregation  
✅ **Promtail** - Automatic log shipping from all nodes  
✅ **Exporters** - PostgreSQL and Redis metrics  
✅ **Alert Rules** - 8 pre-configured critical/warning alerts  
✅ **Annotations** - Prometheus scraping configuration  

**Files created:**
- `10-monitoring-namespace.yaml` - Namespace, configs, storage
- `11-prometheus.yaml` - Prometheus + AlertManager
- `12-grafana.yaml` - Grafana with data sources
- `13-loki.yaml` - Loki + Promtail DaemonSet
- `14-service-monitors.yaml` - DB/Cache exporters
- `MONITORING-GUIDE.md` - This comprehensive guide

**Access URLs (port-forward):**
- **Prometheus:** `http://localhost:9090`
- **AlertManager:** `http://localhost:9093`
- **Grafana:** `http://localhost:3000` (admin/admin)
- **Loki:** `http://localhost:3100`

**Your portfolio now demonstrates:**
- Complete observability implementation
- Production-ready monitoring stack
- Metrics, logs, and alerts
- Custom business metrics
- Database and cache monitoring
- Alert configuration and routing
- Dashboard creation and visualization
