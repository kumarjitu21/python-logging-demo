# Azure Log Analytics Setup Guide

Complete guide to set up Azure Log Analytics workspace and integrate with Fluent Bit.

## Prerequisites

- Azure subscription with contributor access
- Azure CLI installed: `az --version`
- kubectl installed: `kubectl version`
- Running Kubernetes cluster (AKS, Docker Desktop, minikube, etc.)

## Quick Start

```bash
# Login to Azure
az login

# Run setup script
chmod +x k8s/setup-azure.sh
./k8s/setup-azure.sh

# Source credentials
source .azure-credentials

# Deploy application
chmod +x k8s/deploy.sh
./k8s/deploy.sh
```

## Manual Setup Steps

### Step 1: Login to Azure

```bash
az login

# Set subscription (if you have multiple)
az account set --subscription <subscription-id>

# Verify
az account show
```

### Step 2: Create Resource Group

```bash
export RESOURCE_GROUP="fastapi-logs-rg"
export LOCATION="eastus"

az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION"
```

### Step 3: Create Log Analytics Workspace

```bash
export WORKSPACE_NAME="fastapi-logs-workspace"

az monitor log-analytics workspace create \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$WORKSPACE_NAME"
```

### Step 4: Get Workspace Credentials

```bash
# Get Workspace ID (Customer ID)
export WORKSPACE_ID=$(az monitor log-analytics workspace show \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$WORKSPACE_NAME" \
    --query customerId -o tsv)

echo "Workspace ID: $WORKSPACE_ID"

# Get Primary Shared Key
export WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$WORKSPACE_NAME" \
    --query primarySharedKey -o tsv)

echo "Workspace Key: ${WORKSPACE_KEY:0:10}... (hidden for security)"
```

### Step 5: Create Kubernetes Secret

```bash
kubectl delete secret azure-credentials -n fluent-bit --ignore-not-found

kubectl create secret generic azure-credentials \
    --from-literal=workspace-id="${WORKSPACE_ID}" \
    --from-literal=shared-key="${WORKSPACE_KEY}" \
    -n fluent-bit
```

### Step 6: Deploy Fluent Bit

```bash
# Create namespace and RBAC
kubectl apply -f k8s/fluent-bit-namespace.yaml
kubectl apply -f k8s/fluent-bit-serviceaccount.yaml
kubectl apply -f k8s/fluent-bit-clusterrole.yaml
kubectl apply -f k8s/fluent-bit-clusterrolebinding.yaml

# Deploy ConfigMap and DaemonSet
kubectl apply -f k8s/fluent-bit-configmap.yaml
kubectl apply -f k8s/fluent-bit-daemonset.yaml

# Verify deployment
kubectl rollout status daemonset/fluent-bit -n fluent-bit
```

## Verify Log Collection

### Check Fluent Bit Status

```bash
# Get pods
kubectl get pods -n fluent-bit

# Check logs
kubectl logs -n fluent-bit -l app=fluent-bit --tail=20

# Check specific pod
kubectl logs -n fluent-bit <pod-name> -f
```

### Test Log Pipeline

1. Create a test pod:
```bash
kubectl run test-pod \
    --image=alpine \
    --namespace=fastapi-app \
    -- echo "Test log message"
```

2. Wait a few seconds for log to be collected

3. Query in Azure Log Analytics:
```kusto
FastAPILogs
| where TimeGenerated > ago(5m)
| limit 50
```

## Azure Portal Access

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Log Analytics workspaces"
3. Select your workspace
4. Click "Logs" in the left sidebar
5. Run KQL queries

## KQL (Kusto Query Language) Basics

### Basic Query
```kusto
FastAPILogs
```

### Filter by Level
```kusto
FastAPILogs
| where level == "ERROR"
```

### Filter by Time
```kusto
FastAPILogs
| where TimeGenerated > ago(1h)
```

### Summarize
```kusto
FastAPILogs
| summarize count() by level
```

### Time Series
```kusto
FastAPILogs
| where message contains "Response sent"
| summarize request_count=count() by bin(TimeGenerated, 1m)
```

## Common Queries

### 1. All Logs with Timestamps
```kusto
FastAPILogs
| project TimeGenerated, level, message, k8s_pod_name
| order by TimeGenerated desc
| limit 100
```

### 2. Error Analysis
```kusto
FastAPILogs
| where level == "ERROR"
| summarize error_count=count(), last_error=max(TimeGenerated) by message, k8s_pod_name
| order by error_count desc
```

### 3. Request Performance
```kusto
FastAPILogs
| where message contains "Response sent"
| extend latency=tofloat(process_time_ms)
| summarize 
    avg_latency=avg(latency),
    max_latency=max(latency),
    p95_latency=percentile(latency, 95),
    p99_latency=percentile(latency, 99)
    by k8s_pod_name
```

### 4. Request Rate
```kusto
FastAPILogs
| where message contains "Incoming request"
| summarize request_count=count() by bin(TimeGenerated, 1m), k8s_pod_name
| render timechart
```

### 5. Pod Health
```kusto
FastAPILogs
| summarize
    total_logs=count(),
    errors=countif(level == "ERROR"),
    warnings=countif(level == "WARNING"),
    last_log=max(TimeGenerated)
    by k8s_pod_name
```

### 6. Endpoint Analysis
```kusto
FastAPILogs
| where message contains "Incoming request" or message contains "Response sent"
| summarize count() by path
| order by count_ desc
```

### 7. Status Codes
```kusto
FastAPILogs
| where message contains "Response sent"
| extend status=status_code
| summarize count() by status
| render barchart
```

## Create Alerts

### Alert on Error Rate

```bash
# Get workspace resource ID
WORKSPACE_RESOURCE_ID=$(az monitor log-analytics workspace show \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$WORKSPACE_NAME" \
    --query id -o tsv)

# Create alert rule
az monitor metrics alert create \
    --resource-group "$RESOURCE_GROUP" \
    --name "FastAPI High Error Rate" \
    --scopes "$WORKSPACE_RESOURCE_ID" \
    --condition "avg MyMetric > 5" \
    --description "Alert when error rate exceeds 5%"
```

### Alert via Portal

1. In Log Analytics → Alerts → New alert rule
2. Set condition: `FastAPILogs | where level == "ERROR" | count`
3. Set threshold: count > 10
4. Set action group (email, webhook, etc.)

## Dashboards

### Create Dashboard

1. In Log Analytics → Workbooks
2. Click "+ New"
3. Edit and add queries
4. Pin to dashboard

### Example Dashboard Queries

```kusto
FastAPILogs
| where TimeGenerated > ago(24h)
| summarize request_count=count() by bin(TimeGenerated, 1h)
| render timechart with (title="Requests per Hour")
```

```kusto
FastAPILogs
| where level == "ERROR"
| summarize count() by k8s_pod_name
| render piechart with (title="Errors by Pod")
```

## Cost Optimization

### Data Retention
```bash
# Set retention to 30 days
az monitor log-analytics workspace update \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$WORKSPACE_NAME" \
    --retention-time 30
```

### Archive to Storage
```bash
# Create storage account
az storage account create \
    --name <storage-name> \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION"

# Setup archive
az monitor log-analytics workspace data-export create \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$WORKSPACE_NAME" \
    --data-export-name "archive" \
    --destination "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<storage>" \
    --enable true \
    --table "FastAPILogs"
```

## Troubleshooting

### No Logs Appearing

1. Check Fluent Bit is running:
```bash
kubectl get pods -n fluent-bit
kubectl logs -n fluent-bit -l app=fluent-bit
```

2. Verify Azure credentials:
```bash
kubectl get secret azure-credentials -n fluent-bit -o yaml
```

3. Check workspace is accessible:
```bash
az monitor log-analytics workspace show \
    --resource-group "$RESOURCE_GROUP" \
    --workspace-name "$WORKSPACE_NAME"
```

4. Check application is logging:
```bash
kubectl logs -n fastapi-app -l app=fastapi-app
```

### Query Returns No Results

1. Check table name:
```kusto
union withsource=table *
| where TimeGenerated > ago(1h)
| distinct table
```

2. Check time range - logs might be older
3. Check if logs are being collected:
```kusto
FastAPILogs
| summarize count() by TimeGenerated
```

### High Costs

1. Check data ingestion:
```kusto
_BilledSize
| where TimeGenerated > ago(1d)
| summarize total=sum(_BilledSize) by Type
```

2. Reduce retention or archive to storage
3. Filter out unnecessary logs in Fluent Bit config

## Integration with Other Tools

### Grafana
1. Add Azure Monitor data source
2. Create dashboards with Log Analytics queries

### Datadog
1. Set up Azure integration in Datadog
2. Configure log forwarding

### Splunk
1. Use Splunk Connect for Kubernetes
2. Forward logs to Splunk instead of Azure

## References

- [Azure Log Analytics](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-overview)
- [KQL Documentation](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Azure CLI Reference](https://learn.microsoft.com/en-us/cli/azure/)
- [Fluent Bit Azure Output](https://docs.fluentbit.io/manual/pipeline/outputs/azure)
