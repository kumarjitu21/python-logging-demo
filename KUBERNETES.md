# Kubernetes Deployment Guide

This guide covers deploying the FastAPI application with Fluent Bit log aggregation to Azure Kubernetes Service (AKS) with Azure Log Analytics integration.

## Prerequisites

### Required Tools
- `kubectl` (v1.24+)
- `az` CLI (Azure CLI)
- Docker (for building images)
- `helm` (optional, for Fluent Bit Helm charts)

### Azure Resources
- Azure subscription with contributor access
- AKS cluster (or any Kubernetes cluster)
- Azure Log Analytics workspace (will be created by setup script)

## Architecture

```
FastAPI Pod 1/2/3 (emits logs)
         ↓
Kubernetes Container Runtime
         ↓
Fluent Bit DaemonSet (collects logs from all nodes)
         ↓
Azure Log Analytics Workspace
         ↓
KQL Queries & Dashboards
```

## Step 1: Build and Push Docker Image

### Build locally
```bash
docker build -t fastapi-logging-demo:v1.0 .
```

### Push to container registry (ACR)
```bash
# Login to ACR
az acr login --name <your-acr-name>

# Tag image
docker tag fastapi-logging-demo:v1.0 <your-acr-name>.azurecr.io/fastapi-logging-demo:v1.0

# Push image
docker push <your-acr-name>.azurecr.io/fastapi-logging-demo:v1.0
```

## Step 2: Setup Azure Log Analytics

Run the setup script to create Log Analytics workspace and Fluent Bit:

```bash
# Make script executable
chmod +x k8s/setup-azure.sh

# Run setup
./k8s/setup-azure.sh
```

This script will:
1. Create an Azure resource group
2. Create a Log Analytics workspace
3. Setup Azure credentials
4. Deploy Fluent Bit DaemonSet
5. Show sample KQL queries

### Manual Setup (if needed)

```bash
# Create resource group
az group create --name fastapi-logs-rg --location eastus

# Create Log Analytics workspace
az monitor log-analytics workspace create \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace

# Get workspace credentials (save these!)
az monitor log-analytics workspace show \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace \
    --query customerId -o tsv

az monitor log-analytics workspace get-shared-keys \
    --resource-group fastapi-logs-rg \
    --workspace-name fastapi-logs-workspace \
    --query primarySharedKey -o tsv
```

## Step 3: Deploy FastAPI Application

### Quick Deploy
```bash
# Make script executable
chmod +x k8s/deploy.sh

# Deploy application
./k8s/deploy.sh
```

### Manual Deployment
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create config
kubectl apply -f k8s/fastapi-configmap.yaml

# Deploy service
kubectl apply -f k8s/fastapi-service.yaml

# Deploy application
kubectl apply -f k8s/fastapi-deployment.yaml

# Setup auto-scaling
kubectl apply -f k8s/fastapi-hpa.yaml

# Setup pod disruption budget
kubectl apply -f k8s/fastapi-pdb.yaml
```

## Step 4: Verify Deployment

```bash
# Check pod status
kubectl get pods -n fastapi-app

# Check service
kubectl get service fastapi-app -n fastapi-app

# Get external IP
kubectl get service fastapi-app -n fastapi-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# View logs
kubectl logs -n fastapi-app -l app=fastapi-app -f
```

## Step 5: Verify Fluent Bit Logs

```bash
# Check Fluent Bit pods
kubectl get pods -n fluent-bit

# Check Fluent Bit logs
kubectl logs -n fluent-bit -l app=fluent-bit -f

# Access Fluent Bit metrics
kubectl port-forward -n fluent-bit daemonset/fluent-bit 2020:2020
# Then visit: http://localhost:2020/api/v1/metrics/prometheus
```

## Step 6: Query Logs in Azure Log Analytics

Go to Azure Portal → Log Analytics Workspace → Logs

### Sample Queries

**All logs:**
```kusto
FastAPILogs
```

**Recent errors:**
```kusto
FastAPILogs
| where level == "ERROR"
| order by timestamp desc
| limit 50
```

**Request latency:**
```kusto
FastAPILogs
| where message contains "Response sent"
| extend process_time = process_time_ms
| summarize avg_latency=avg(tonumber(process_time)), max_latency=max(tonumber(process_time)) by k8s_pod_name
```

**Error rate by endpoint:**
```kusto
FastAPILogs
| where level == "ERROR"
| summarize error_count=count() by path
| order by error_count desc
```

**Requests per second:**
```kusto
FastAPILogs
| where message contains "Incoming request"
| summarize requests=count() by bin(timestamp, 1s), k8s_pod_name
```

## Kubernetes Manifests Overview

### Files
- `namespace.yaml` - FastAPI namespace
- `fastapi-configmap.yaml` - Application configuration
- `fastapi-service.yaml` - LoadBalancer service
- `fastapi-deployment.yaml` - Application deployment (3 replicas)
- `fastapi-hpa.yaml` - Horizontal Pod Autoscaler (3-10 replicas)
- `fastapi-pdb.yaml` - Pod Disruption Budget (min 2 available)

### Fluent Bit Files
- `fluent-bit-namespace.yaml` - Fluent Bit namespace
- `fluent-bit-serviceaccount.yaml` - Service account
- `fluent-bit-clusterrole.yaml` - Cluster role
- `fluent-bit-clusterrolebinding.yaml` - Role binding
- `fluent-bit-configmap.yaml` - Fluent Bit configuration
- `fluent-bit-daemonset.yaml` - DaemonSet deployment

## Environment Variables

### Application
- `DEBUG` - Debug mode (True/False)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `APP_NAME` - Application name
- `ENVIRONMENT` - Deployment environment

### Fluent Bit
- `AZURE_WORKSPACE_ID` - Log Analytics workspace ID
- `AZURE_WORKSPACE_KEY` - Log Analytics shared key
- `CLUSTER_NAME` - Kubernetes cluster name
- `ENVIRONMENT` - Environment (production, staging, etc.)

## Scaling

### Manual Scaling
```bash
kubectl scale deployment/fastapi-app --replicas=5 -n fastapi-app
```

### Auto Scaling
The HPA is configured to scale based on:
- CPU utilization > 70%
- Memory utilization > 80%
- Min replicas: 3
- Max replicas: 10

Check HPA status:
```bash
kubectl get hpa fastapi-app -n fastapi-app
```

## Updates and Rollbacks

### Rolling Update
```bash
# Update image
kubectl set image deployment/fastapi-app \
    fastapi=your-registry/fastapi-logging-demo:v1.1 \
    -n fastapi-app

# Monitor rollout
kubectl rollout status deployment/fastapi-app -n fastapi-app
```

### Rollback
```bash
kubectl rollout undo deployment/fastapi-app -n fastapi-app
```

## Monitoring

### Check deployment status
```bash
kubectl describe deployment fastapi-app -n fastapi-app
```

### Pod events
```bash
kubectl get events -n fastapi-app --sort-by='.lastTimestamp'
```

### Resource usage
```bash
kubectl top pods -n fastapi-app
kubectl top nodes
```

## Troubleshooting

### Pod won't start
```bash
kubectl describe pod <pod-name> -n fastapi-app
kubectl logs <pod-name> -n fastapi-app
```

### Service not accessible
```bash
# Check service endpoints
kubectl get endpoints fastapi-app -n fastapi-app

# Check ingress/load balancer
kubectl get svc -n fastapi-app
```

### Logs not appearing in Azure
```bash
# Check Fluent Bit pods
kubectl get pods -n fluent-bit

# Check Fluent Bit logs
kubectl logs -n fluent-bit -l app=fluent-bit --tail=50

# Verify Azure credentials secret
kubectl get secret azure-credentials -n fluent-bit
```

### Performance issues
```bash
# Check resource limits
kubectl get deployment fastapi-app -n fastapi-app -o yaml | grep -A 5 resources

# Check current usage
kubectl top pods -n fastapi-app

# Adjust limits in fastapi-deployment.yaml if needed
```

## Cleanup

### Delete application
```bash
kubectl delete namespace fastapi-app
```

### Delete Fluent Bit
```bash
kubectl delete namespace fluent-bit
```

### Delete Azure resources
```bash
az group delete --name fastapi-logs-rg --yes
```

## Production Checklist

- [ ] Docker image pushed to private registry
- [ ] Azure Log Analytics workspace created
- [ ] Fluent Bit credentials stored securely
- [ ] Deployment replicas set appropriately
- [ ] HPA configured for your workload
- [ ] PDB configured for high availability
- [ ] Resource limits defined
- [ ] Health checks configured
- [ ] Security policies applied
- [ ] Network policies configured (if needed)
- [ ] Persistent volume for logs (if needed)
- [ ] Backup strategy for logs
- [ ] Monitoring/alerting configured
- [ ] Log retention policy set

## Additional Resources

- [Azure Kubernetes Service (AKS)](https://learn.microsoft.com/en-us/azure/aks/)
- [Fluent Bit Documentation](https://docs.fluentbit.io/)
- [Azure Log Analytics KQL](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
