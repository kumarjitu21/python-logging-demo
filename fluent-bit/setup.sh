#!/bin/bash
# Setup Fluent Bit for Azure Log Analytics

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Fluent Bit Setup for Azure Log Analytics${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Check if required environment variables are set
check_required_vars() {
    local vars=("AZURE_WORKSPACE_ID" "AZURE_WORKSPACE_KEY" "CLUSTER_NAME" "ENVIRONMENT")
    
    for var in "${vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo -e "${RED}Error: ${var} environment variable is not set${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✓ All required environment variables are set${NC}\n"
}

# Create namespace
create_namespace() {
    echo -e "${YELLOW}Creating fluent-bit namespace...${NC}"
    
    kubectl create namespace fluent-bit --dry-run=client -o yaml | kubectl apply -f -
    
    echo -e "${GREEN}✓ Namespace created${NC}\n"
}

# Create secret for Azure credentials
create_azure_secret() {
    echo -e "${YELLOW}Creating Azure credentials secret...${NC}"
    
    kubectl delete secret azure-credentials -n fluent-bit --ignore-not-found
    
    kubectl create secret generic azure-credentials \
        --from-literal=workspace-id="${AZURE_WORKSPACE_ID}" \
        --from-literal=shared-key="${AZURE_WORKSPACE_KEY}" \
        -n fluent-bit
    
    echo -e "${GREEN}✓ Azure secret created${NC}\n"
}

# Deploy Fluent Bit
deploy_fluent_bit() {
    echo -e "${YELLOW}Deploying Fluent Bit...${NC}"
    
    kubectl apply -f k8s/fluent-bit-namespace.yaml
    kubectl apply -f k8s/fluent-bit-serviceaccount.yaml
    kubectl apply -f k8s/fluent-bit-clusterrole.yaml
    kubectl apply -f k8s/fluent-bit-clusterrolebinding.yaml
    kubectl apply -f k8s/fluent-bit-configmap.yaml
    kubectl apply -f k8s/fluent-bit-daemonset.yaml
    
    echo -e "${GREEN}✓ Fluent Bit deployed${NC}\n"
}

# Verify deployment
verify_deployment() {
    echo -e "${YELLOW}Verifying deployment...${NC}"
    
    # Wait for pods to be ready
    kubectl rollout status daemonset/fluent-bit -n fluent-bit --timeout=300s
    
    echo -e "${GREEN}✓ Deployment verified${NC}\n"
}

# Show deployment status
show_status() {
    echo -e "${YELLOW}Fluent Bit Deployment Status:${NC}"
    echo ""
    kubectl get pods -n fluent-bit
    echo ""
    echo -e "${YELLOW}Checking logs:${NC}"
    kubectl logs -n fluent-bit -l app=fluent-bit --tail=20
}

# Main execution
main() {
    check_required_vars
    create_namespace
    create_azure_secret
    deploy_fluent_bit
    verify_deployment
    show_status
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Setup complete! Logs are being sent to Azure Log Analytics.${NC}"
    echo -e "${GREEN}========================================${NC}"
}

main "$@"
