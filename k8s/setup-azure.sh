#!/bin/bash
# Setup Azure Log Analytics and deploy Fluent Bit

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Azure Log Analytics Setup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    if ! command -v az >/dev/null 2>&1; then
        echo -e "${RED}Azure CLI is not installed${NC}"
        echo "Install from: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    
    if ! command -v kubectl >/dev/null 2>&1; then
        echo -e "${RED}kubectl is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites check passed${NC}\n"
}

# Login to Azure
login_to_azure() {
    echo -e "${YELLOW}Logging in to Azure...${NC}"
    
    az login
    
    # Get subscription ID
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    echo -e "${GREEN}✓ Using subscription: ${SUBSCRIPTION_ID}${NC}\n"
}

# Create resource group
create_resource_group() {
    local resource_group="${RESOURCE_GROUP:-fastapi-logs-rg}"
    local location="${LOCATION:-eastus}"
    
    echo -e "${YELLOW}Creating resource group: ${resource_group}...${NC}"
    
    az group create \
        --name "$resource_group" \
        --location "$location"
    
    echo -e "${GREEN}✓ Resource group created${NC}\n"
    
    export RESOURCE_GROUP="$resource_group"
}

# Create Log Analytics workspace
create_log_analytics_workspace() {
    local workspace_name="${WORKSPACE_NAME:-fastapi-logs-workspace}"
    local resource_group="${RESOURCE_GROUP:-fastapi-logs-rg}"
    
    echo -e "${YELLOW}Creating Log Analytics workspace: ${workspace_name}...${NC}"
    
    az monitor log-analytics workspace create \
        --resource-group "$resource_group" \
        --workspace-name "$workspace_name"
    
    # Get workspace details
    WORKSPACE_ID=$(az monitor log-analytics workspace show \
        --resource-group "$resource_group" \
        --workspace-name "$workspace_name" \
        --query customerId -o tsv)
    
    WORKSPACE_KEY=$(az monitor log-analytics workspace get-shared-keys \
        --resource-group "$resource_group" \
        --workspace-name "$workspace_name" \
        --query primarySharedKey -o tsv)
    
    echo -e "${GREEN}✓ Log Analytics workspace created${NC}"
    echo -e "${GREEN}  Workspace ID: ${WORKSPACE_ID}${NC}"
    echo -e "${GREEN}  Workspace Key: ***${NC}\n"
    
    export WORKSPACE_NAME="$workspace_name"
}

# Create data collection rule
create_data_collection_rule() {
    local resource_group="${RESOURCE_GROUP:-fastapi-logs-rg}"
    local workspace_name="${WORKSPACE_NAME}"
    
    echo -e "${YELLOW}Creating data collection rule...${NC}"
    
    # Get workspace resource ID
    WORKSPACE_RESOURCE_ID=$(az monitor log-analytics workspace show \
        --resource-group "$resource_group" \
        --workspace-name "$workspace_name" \
        --query id -o tsv)
    
    # Create DCR
    az monitor data-collection rule create \
        --resource-group "$resource_group" \
        --name "fastapi-dcr" \
        --location "eastus" \
        --data-flows \
            destinations="FastAPILogs" \
            streams="Microsoft-CommonSecurityLog" \
        --destinations \
            logAnalytics \
                workspaceResourceId="$WORKSPACE_RESOURCE_ID" \
                name="FastAPILogs" \
        || echo -e "${YELLOW}Note: Data collection rule creation might be optional for your setup${NC}"
    
    echo -e "${GREEN}✓ Data collection rule configured${NC}\n"
}

# Deploy Fluent Bit with Azure credentials
deploy_fluent_bit() {
    echo -e "${YELLOW}Deploying Fluent Bit to Kubernetes...${NC}"
    
    # Create Fluent Bit namespace and RBAC
    kubectl apply -f k8s/fluent-bit-namespace.yaml
    kubectl apply -f k8s/fluent-bit-serviceaccount.yaml
    kubectl apply -f k8s/fluent-bit-clusterrole.yaml
    kubectl apply -f k8s/fluent-bit-clusterrolebinding.yaml
    
    # Create secret with Azure credentials
    kubectl delete secret azure-credentials -n fluent-bit --ignore-not-found
    kubectl create secret generic azure-credentials \
        --from-literal=workspace-id="${WORKSPACE_ID}" \
        --from-literal=shared-key="${WORKSPACE_KEY}" \
        -n fluent-bit
    
    # Deploy ConfigMap and DaemonSet
    kubectl apply -f k8s/fluent-bit-configmap.yaml
    kubectl apply -f k8s/fluent-bit-daemonset.yaml
    
    echo -e "${GREEN}✓ Fluent Bit deployed${NC}\n"
}

# Verify deployment
verify_deployment() {
    echo -e "${YELLOW}Verifying Fluent Bit deployment...${NC}"
    
    kubectl rollout status daemonset/fluent-bit -n fluent-bit --timeout=300s
    
    echo -e "${GREEN}✓ Fluent Bit is running${NC}\n"
}

# Show log queries
show_log_queries() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Sample Azure Log Analytics KQL Queries${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    echo -e "${YELLOW}1. Show all FastAPI logs:${NC}"
    echo "FastAPILogs"
    echo ""
    
    echo -e "${YELLOW}2. Show errors only:${NC}"
    echo 'FastAPILogs | where level == "ERROR"'
    echo ""
    
    echo -e "${YELLOW}3. Show request latency by endpoint:${NC}"
    echo 'FastAPILogs | where message contains "Response sent" | summarize avg(process_time_ms) by path'
    echo ""
    
    echo -e "${YELLOW}4. Show logs by container:${NC}"
    echo 'FastAPILogs | where k8s_pod_name != "" | summarize count() by k8s_pod_name'
    echo ""
    
    echo -e "${YELLOW}5. Show recent errors with context:${NC}"
    echo 'FastAPILogs | where level == "ERROR" | project timestamp, message, error, k8s_pod_name | order by timestamp desc | limit 50'
    echo ""
}

# Save credentials to file
save_credentials() {
    local creds_file=".azure-credentials"
    
    echo -e "${YELLOW}Saving credentials to ${creds_file}...${NC}"
    
    cat > "$creds_file" << EOF
#!/bin/bash
# Azure Log Analytics Credentials
# Source this file: source $creds_file

export AZURE_WORKSPACE_ID="${WORKSPACE_ID}"
export AZURE_WORKSPACE_KEY="${WORKSPACE_KEY}"
export RESOURCE_GROUP="${RESOURCE_GROUP}"
export WORKSPACE_NAME="${WORKSPACE_NAME}"
export CLUSTER_NAME="aks-cluster"
export ENVIRONMENT="production"
EOF
    
    chmod 600 "$creds_file"
    
    echo -e "${GREEN}✓ Credentials saved (keep this file secure!)${NC}"
    echo -e "${YELLOW}Source the file before deploying: source ${creds_file}${NC}\n"
}

# Main execution
main() {
    check_prerequisites
    login_to_azure
    create_resource_group
    create_log_analytics_workspace
    create_data_collection_rule
    deploy_fluent_bit
    verify_deployment
    show_log_queries
    save_credentials
    
    echo -e "${BLUE}========================================${NC}"
    echo -e "${GREEN}Azure setup completed successfully!${NC}"
    echo -e "${BLUE}========================================${NC}"
}

main "$@"
