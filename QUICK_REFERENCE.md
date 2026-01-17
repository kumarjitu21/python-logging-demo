# Quick Reference Guide

## 📚 Documentation Map

```
START HERE → README.md (5 min overview)
    ↓
Choose your path:
├── Local Development → README.md + Makefile
├── Docker Setup → README.md + Dockerfile + docker-compose.yml
├── Kubernetes → KUBERNETES.md + k8s/
└── Azure Cloud → AZURE.md + DEPLOYMENT.md
```

## 🎯 Common Tasks

### Setup Local Development
```bash
poetry install
poetry run pytest tests/
poetry run uvicorn app.main:app --reload
```

### Build & Run Docker
```bash
docker build -t fastapi-logging-demo:v1.0 .
docker-compose up
```

### Deploy to Kubernetes
```bash
./k8s/deploy.sh
```

### Setup Azure Log Analytics
```bash
./k8s/setup-azure.sh
```

### View Logs
```bash
# Local
tail -f logs/app.log

# Container
docker logs <container-id> -f

# Kubernetes
kubectl logs -n fastapi-app -l app=fastapi-app -f

# Azure Portal
# Go to Log Analytics Workspace → Logs
# Query: FastAPILogs
```

## 📂 File Reference

| File | Purpose | Usage |
|------|---------|-------|
| app/main.py | FastAPI app entry | Application code |
| app/api/routes.py | API endpoints | Endpoint implementation |
| app/core/logging.py | Loguru setup | Logging configuration |
| k8s/deploy.sh | K8s deployment | `./k8s/deploy.sh` |
| k8s/setup-azure.sh | Azure setup | `./k8s/setup-azure.sh` |
| fluent-bit/fluent-bit.conf | Fluent Bit config | Log collection |
| Dockerfile | Container image | `docker build` |
| docker-compose.yml | Local Docker | `docker-compose up` |

## 🔗 Key Endpoints

```
Application
├── GET / → Root info
├── GET /docs → Swagger UI
├── GET /redoc → ReDoc docs
└── /api/
    ├── GET /health → Health check
    └── /users
        ├── POST / → Create user
        ├── GET / → List users
        ├── GET /{id} → Get user
        ├── PUT /{id} → Update user
        └── DELETE /{id} → Delete user
```

## 🐳 Docker Commands

```bash
# Build
docker build -t fastapi-logging-demo:v1.0 .

# Run
docker run -p 8000:8000 fastapi-logging-demo:v1.0

# Compose
docker-compose up
docker-compose down

# Registry push
docker push <registry>/fastapi-logging-demo:v1.0

# Logs
docker logs <container> -f
```

## ☸️ Kubernetes Commands

```bash
# Deploy
kubectl apply -f k8s/

# Status
kubectl get pods -n fastapi-app
kubectl get svc -n fastapi-app

# Logs
kubectl logs -n fastapi-app -l app=fastapi-app -f

# Port forward
kubectl port-forward -n fastapi-app svc/fastapi-app 8000:80

# Scale
kubectl scale deployment fastapi-app --replicas=5 -n fastapi-app

# Rollout
kubectl rollout status deployment/fastapi-app -n fastapi-app
kubectl rollout undo deployment/fastapi-app -n fastapi-app
```

## ☁️ Azure Commands

```bash
# Login
az login

# Create resource group
az group create --name fastapi-logs-rg --location eastus

# Create Log Analytics
az monitor log-analytics workspace create \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace

# Get credentials
az monitor log-analytics workspace show --query customerId -o tsv
az monitor log-analytics workspace get-shared-keys --query primarySharedKey -o tsv

# Cleanup
az group delete --name fastapi-logs-rg --yes
```

## 📊 KQL Query Templates

```kusto
# All logs
FastAPILogs

# Recent errors
FastAPILogs | where level == "ERROR" | limit 50

# Request latency
FastAPILogs 
| where message contains "Response sent"
| extend latency=tofloat(process_time_ms)
| summarize avg=avg(latency) by k8s_pod_name

# Request rate
FastAPILogs 
| where message contains "Incoming request"
| summarize count() by bin(TimeGenerated, 1m)

# Pod health
FastAPILogs
| summarize 
    logs=count(),
    errors=countif(level=="ERROR"),
    last_log=max(TimeGenerated)
    by k8s_pod_name
```

## 🐛 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Tests failing | See README.md → Testing |
| App won't start | Check logs, see DEPLOYMENT.md |
| No logs in Azure | See KUBERNETES.md → Troubleshooting |
| Pod not ready | `kubectl describe pod <name>` |
| Service not accessible | `kubectl get endpoints` |
| High memory usage | Check Fluent Bit buffer limits |

## 📈 Performance Tuning

```bash
# Check resource usage
kubectl top pods -n fastapi-app
kubectl top nodes

# Check HPA status
kubectl get hpa -n fastapi-app
kubectl describe hpa fastapi-app -n fastapi-app

# Adjust replicas
kubectl scale deployment fastapi-app --replicas=5 -n fastapi-app

# Check logs size
du -sh logs/

# Adjust retention
az monitor log-analytics workspace update \
    --retention-time 30
```

## 🔐 Security Checklist

- [ ] Azure credentials in environment (not in code)
- [ ] Docker image scanned for vulnerabilities
- [ ] Kubernetes RBAC configured
- [ ] Network policies applied (if needed)
- [ ] Pod security policies enabled (if needed)
- [ ] Secrets stored in Kubernetes secrets
- [ ] Registry access controlled
- [ ] Audit logging enabled

## 📚 Documentation Index

1. **README.md** - Start here
2. **PROJECT_SUMMARY.md** - Overview of everything
3. **DEPLOYMENT.md** - Step-by-step deployment
4. **KUBERNETES.md** - K8s details
5. **FLUENT_BIT.md** - Log aggregation
6. **AZURE.md** - Cloud setup
7. **LOGGING.md** - Logging config
8. **CHECKLIST.md** - Completion checklist
9. **QUICK_REFERENCE.md** - This file

## 🚀 Deployment Paths

### Local Development (5 min)
```
1. poetry install
2. poetry run pytest
3. poetry run uvicorn app.main:app --reload
```

### Docker Local (10 min)
```
1. docker-compose up
2. curl http://localhost:8000/api/health
```

### Kubernetes Dev (20 min)
```
1. ./k8s/deploy.sh
2. kubectl get pods -n fastapi-app
```

### Full Cloud Stack (30 min)
```
1. ./k8s/setup-azure.sh
2. ./k8s/deploy.sh
3. Query logs in Azure Portal
```

## 💡 Tips & Tricks

```bash
# Watch resources in real-time
watch kubectl get pods -n fastapi-app

# Tail logs with timestamps
kubectl logs -n fastapi-app -l app=fastapi-app -f --timestamps=true

# Get pod shell access
kubectl exec -it <pod-name> -n fastapi-app -- /bin/bash

# Copy files from pod
kubectl cp fastapi-app/<pod>:/app/logs/app.log ./

# Get deployment yaml
kubectl get deployment fastapi-app -n fastapi-app -o yaml

# Dry-run before applying
kubectl apply -f k8s/ --dry-run=client

# Format output as JSON
kubectl get pods -n fastapi-app -o json | jq '.items[0]'
```

## 📞 Getting Help

1. **Quick Issues** → Check DEPLOYMENT.md troubleshooting
2. **K8s Problems** → See KUBERNETES.md
3. **Azure Issues** → Reference AZURE.md
4. **Logging Config** → Check LOGGING.md
5. **General Info** → Read PROJECT_SUMMARY.md

---

**Version:** 0.1.0  
**Last Updated:** January 2024  
**Status:** ✅ Ready for Production
