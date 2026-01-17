# Complete Deployment Guide

This guide provides a step-by-step walkthrough for deploying the FastAPI logging application with Fluent Bit and Azure Log Analytics integration.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Containerization](#docker-containerization)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Azure Setup](#azure-setup)
5. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
6. [Production Best Practices](#production-best-practices)

## Local Development

### Prerequisites

- Python 3.9+
- Poetry
- Git

### Setup

```bash
# Clone or navigate to project
cd python-logging-demo

# Install dependencies
poetry install

# Create environment file (optional)
cp .env.example .env
```

### Run Locally

```bash
# Development with auto-reload
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production-like
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Application

- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/health

### View Logs

```bash
# Console logs (real-time)
tail -f logs/app.log

# Error logs
tail -f logs/errors.log

# Structured JSON logs
tail -f logs/structured.json

# Pretty-print JSON
cat logs/structured.json | python -m json.tool
```

### Run Tests

```bash
# All tests
poetry run pytest tests/ -v

# With coverage
poetry run pytest tests/ --cov=app

# Specific test
poetry run pytest tests/test_api.py::test_health_check -v
```

## Docker Containerization

### Build Image

```bash
# Build locally
docker build -t fastapi-logging-demo:v1.0 .

# With build args
docker build -t fastapi-logging-demo:v1.0 \
    --build-arg PYTHON_VERSION=3.11 \
    .
```

### Run Container Locally

```bash
# Run container
docker run -p 8000:8000 \
    -e DEBUG=False \
    -e LOG_LEVEL=INFO \
    -v $(pwd)/logs:/app/logs \
    fastapi-logging-demo:v1.0

# Run with docker-compose
docker-compose up

# View logs
docker logs <container-id>
docker logs -f <container-id>  # Follow logs

# Stop container
docker-compose down
```

### Push to Registry

```bash
# Login to ACR (Azure Container Registry)
az acr login --name <acr-name>

# Tag image
docker tag fastapi-logging-demo:v1.0 \
    <acr-name>.azurecr.io/fastapi-logging-demo:v1.0

# Push
docker push <acr-name>.azurecr.io/fastapi-logging-demo:v1.0

# Or push to Docker Hub
docker tag fastapi-logging-demo:v1.0 \
    <docker-username>/fastapi-logging-demo:v1.0
docker push <docker-username>/fastapi-logging-demo:v1.0
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (AKS, EKS, GKE, or local with Docker Desktop)
- `kubectl` configured
- Container image in registry (or Docker Hub)

### Option 1: Automated Deployment Script

```bash
# Make script executable
chmod +x k8s/deploy.sh

# Deploy with defaults
./k8s/deploy.sh

# Or with custom values
NAMESPACE=my-app IMAGE_NAME=my-image IMAGE_TAG=latest ./k8s/deploy.sh
```

### Option 2: Manual Deployment

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create configuration
kubectl apply -f k8s/fastapi-configmap.yaml

# Create service
kubectl apply -f k8s/fastapi-service.yaml

# Deploy application
kubectl apply -f k8s/fastapi-deployment.yaml

# Setup auto-scaling
kubectl apply -f k8s/fastapi-hpa.yaml

# Setup pod disruption budget
kubectl apply -f k8s/fastapi-pdb.yaml
```

### Verify Deployment

```bash
# Check pods
kubectl get pods -n fastapi-app
kubectl get pods -n fastapi-app -w  # Watch

# Check service
kubectl get svc -n fastapi-app

# Get external IP
kubectl get svc fastapi-app -n fastapi-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Check events
kubectl get events -n fastapi-app

# View pod logs
kubectl logs -n fastapi-app -l app=fastapi-app
kubectl logs -n fastapi-app -l app=fastapi-app -f  # Follow
kubectl logs -n fastapi-app <pod-name> --previous  # Previous pod

# Describe pod
kubectl describe pod <pod-name> -n fastapi-app
```

### Test Deployment

```bash
# Port forward to access locally
kubectl port-forward -n fastapi-app svc/fastapi-app 8000:80

# Test health endpoint
curl http://localhost:8000/api/health | python -m json.tool

# Test create user
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

# View request headers (includes X-Request-ID)
curl -i http://localhost:8000/api/health
```

## Azure Setup

### Step 1: Login to Azure

```bash
# Interactive login
az login

# Or with service principal
az login --service-principal -u <app-id> -p <password> --tenant <tenant-id>

# Check current account
az account show

# Set subscription (if multiple)
az account set --subscription <subscription-id>
```

### Step 2: Create Azure Resources

```bash
# Using automated script
chmod +x k8s/setup-azure.sh
./k8s/setup-azure.sh

# Or manually
# Create resource group
az group create --name fastapi-logs-rg --location eastus

# Create Log Analytics workspace
az monitor log-analytics workspace create \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace

# Get workspace credentials
WORKSPACE_ID=$(az monitor log-analytics workspace show \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace \
    --query customerId -o tsv)

WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace \
    --query primarySharedKey -o tsv)

echo "Workspace ID: $WORKSPACE_ID"
echo "Workspace Key: $WORKSPACE_KEY"
```

### Step 3: Deploy Fluent Bit

```bash
# Create Fluent Bit namespace and RBAC
kubectl apply -f k8s/fluent-bit-namespace.yaml
kubectl apply -f k8s/fluent-bit-serviceaccount.yaml
kubectl apply -f k8s/fluent-bit-clusterrole.yaml
kubectl apply -f k8s/fluent-bit-clusterrolebinding.yaml

# Create secret with Azure credentials
kubectl create secret generic azure-credentials \
    --from-literal=workspace-id="${WORKSPACE_ID}" \
    --from-literal=shared-key="${WORKSPACE_KEY}" \
    -n fluent-bit

# Deploy Fluent Bit
kubectl apply -f k8s/fluent-bit-configmap.yaml
kubectl apply -f k8s/fluent-bit-daemonset.yaml

# Verify
kubectl rollout status daemonset/fluent-bit -n fluent-bit
```

### Step 4: Verify Log Collection

```bash
# Check Fluent Bit pods
kubectl get pods -n fluent-bit

# Check Fluent Bit logs
kubectl logs -n fluent-bit -l app=fluent-bit --tail=20

# Wait for logs to appear in Azure (usually 1-2 minutes)
# Then query in Azure Portal
```

## Monitoring & Troubleshooting

### Monitor Application

```bash
# Pod status and resource usage
kubectl top pods -n fastapi-app
kubectl top nodes

# Describe pod for events
kubectl describe pod <pod-name> -n fastapi-app

# Check HPA status
kubectl get hpa -n fastapi-app
kubectl describe hpa fastapi-app -n fastapi-app

# Scale manually for testing
kubectl scale deployment fastapi-app --replicas=5 -n fastapi-app
```

### Monitor Fluent Bit

```bash
# Pod status
kubectl get pods -n fluent-bit
kubectl logs -n fluent-bit -l app=fluent-bit -f

# Health check
kubectl port-forward -n fluent-bit daemonset/fluent-bit 2020:2020
curl http://localhost:2020/api/v1/health

# Metrics
curl http://localhost:2020/api/v1/metrics/prometheus
```

### Query Logs in Azure

Go to [Azure Portal](https://portal.azure.com) → Log Analytics Workspaces → Your Workspace → Logs

```kusto
# View all logs
FastAPILogs

# Recent errors
FastAPILogs 
| where level == "ERROR" 
| order by TimeGenerated desc 
| limit 50

# Request latency
FastAPILogs 
| where message contains "Response sent"
| extend latency=tofloat(process_time_ms)
| summarize avg=avg(latency), p95=percentile(latency, 95) by k8s_pod_name
```

### Troubleshooting Checklist

**Application not starting:**
```bash
# Check pod status
kubectl describe pod <pod-name> -n fastapi-app

# Check events
kubectl get events -n fastapi-app

# Check logs
kubectl logs <pod-name> -n fastapi-app
kubectl logs <pod-name> -n fastapi-app --previous
```

**No logs in Azure:**
```bash
# Verify Fluent Bit is running
kubectl get pods -n fluent-bit

# Check Fluent Bit logs for errors
kubectl logs -n fluent-bit -l app=fluent-bit

# Verify credentials
kubectl get secret azure-credentials -n fluent-bit -o yaml

# Check if app is logging
kubectl logs -n fastapi-app -l app=fastapi-app
```

**Performance issues:**
```bash
# Check resource usage
kubectl top pods -n fastapi-app
kubectl describe node <node-name>

# Check if HPA is scaling
kubectl get hpa -n fastapi-app -w

# Check pending requests
kubectl top nodes
kubectl get --raw /api/v1/namespaces/fastapi-app/pods
```

**Memory/Disk issues:**
```bash
# Check disk usage
kubectl exec -n fluent-bit <pod> -- df -h

# Reduce Fluent Bit buffer
# Edit ConfigMap and reduce Mem_Buf_Limit

# Check logs retention
az monitor log-analytics workspace update \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace \
    --retention-time 30
```

## Production Best Practices

### Security

```bash
# Use private registry
# Edit fastapi-deployment.yaml:
imagePullSecrets:
  - name: regcred

# Create pull secret
kubectl create secret docker-registry regcred \
    --docker-server=<registry-name>.azurecr.io \
    --docker-username=<username> \
    --docker-password=<password> \
    -n fastapi-app

# Use network policies
kubectl apply -f - << EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: fastapi-app
  namespace: fastapi-app
spec:
  podSelector:
    matchLabels:
      app: fastapi-app
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: fluent-bit
EOF

# Enable pod security policy
# kubectl apply -f pod-security-policy.yaml
```

### Monitoring & Alerts

```bash
# Create email alert for errors
# In Azure Portal → Log Analytics → Alerts → New alert rule
# Condition: FastAPILogs | where level == "ERROR" | count > 10
# Action: Send email

# Export logs to storage for long-term retention
STORAGE_ID=$(az storage account show \
    --name <storage-name> \
    --resource-group fastapi-logs-rg \
    --query id -o tsv)

az monitor log-analytics workspace data-export create \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace \
    --data-export-name archive \
    --destination "$STORAGE_ID/blobServices/default/containers/logs" \
    --enable true \
    --table FastAPILogs
```

### Cost Optimization

```bash
# Set log retention to 30 days
az monitor log-analytics workspace update \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace \
    --retention-time 30

# Set reserved capacity (for predictable costs)
az monitor log-analytics workspace update \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace \
    --sku Premium \
    --capacity-reservation 100
```

### Backup & Disaster Recovery

```bash
# Backup configuration
kubectl get all -n fastapi-app -o yaml > backup-fastapi.yaml
kubectl get all -n fluent-bit -o yaml > backup-fluent-bit.yaml

# Backup Fluent Bit config
kubectl get configmap fluent-bit-config -n fluent-bit -o yaml > fluent-bit-config-backup.yaml

# Restore from backup
kubectl apply -f backup-fastapi.yaml
```

### Updates & Rollouts

```bash
# Update image
kubectl set image deployment/fastapi-app \
    fastapi=<registry>/fastapi-logging-demo:v1.1 \
    -n fastapi-app

# Monitor rollout
kubectl rollout status deployment/fastapi-app -n fastapi-app

# Rollback if issues
kubectl rollout undo deployment/fastapi-app -n fastapi-app

# Check rollout history
kubectl rollout history deployment/fastapi-app -n fastapi-app
```

### Cleanup

```bash
# Delete deployment
kubectl delete namespace fastapi-app

# Delete Fluent Bit
kubectl delete namespace fluent-bit

# Delete Azure resources
az group delete --name fastapi-logs-rg --yes
```

## Summary

This deployment guide covers:
- ✅ Local development setup
- ✅ Docker containerization
- ✅ Kubernetes deployment
- ✅ Azure Log Analytics integration
- ✅ Fluent Bit log aggregation
- ✅ Monitoring and troubleshooting
- ✅ Production best practices

For detailed information, see:
- [README.md](README.md) - Project overview
- [KUBERNETES.md](KUBERNETES.md) - Kubernetes details
- [FLUENT_BIT.md](FLUENT_BIT.md) - Fluent Bit configuration
- [AZURE.md](AZURE.md) - Azure setup details
- [LOGGING.md](LOGGING.md) - Logging configuration
