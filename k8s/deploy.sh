#!/bin/bash
# Deploy FastAPI application to Kubernetes

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
NAMESPACE="${NAMESPACE:-fastapi-app}"
IMAGE_NAME="${IMAGE_NAME:-fastapi-logging-demo}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}FastAPI Application Deployment${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    if ! command_exists kubectl; then
        echo -e "${RED}kubectl is not installed${NC}"
        exit 1
    fi
    
    if ! command_exists docker && [ -z "$REGISTRY" ]; then
        echo -e "${YELLOW}Warning: Docker not found. Make sure image is already in registry.${NC}"
    fi
    
    # Check cluster connectivity
    if ! kubectl cluster-info >/dev/null 2>&1; then
        echo -e "${RED}Cannot connect to Kubernetes cluster${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites check passed${NC}\n"
}

# Build Docker image
build_image() {
    if ! command_exists docker; then
        echo -e "${YELLOW}Skipping Docker build - docker not found${NC}"
        return
    fi
    
    echo -e "${YELLOW}Building Docker image...${NC}"
    
    local image_full_name="${IMAGE_NAME}:${IMAGE_TAG}"
    if [ -n "$REGISTRY" ]; then
        image_full_name="${REGISTRY}/${image_full_name}"
    fi
    
    docker build -t "$image_full_name" .
    
    if [ -n "$REGISTRY" ]; then
        echo -e "${YELLOW}Pushing image to registry...${NC}"
        docker push "$image_full_name"
    fi
    
    echo -e "${GREEN}✓ Image built successfully${NC}\n"
}

# Create namespace
create_namespace() {
    echo -e "${YELLOW}Creating namespace: ${NAMESPACE}...${NC}"
    
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    echo -e "${GREEN}✓ Namespace created${NC}\n"
}

# Deploy application
deploy_application() {
    echo -e "${YELLOW}Deploying application...${NC}"
    
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/fastapi-configmap.yaml
    kubectl apply -f k8s/fastapi-service.yaml
    kubectl apply -f k8s/fastapi-deployment.yaml
    kubectl apply -f k8s/fastapi-hpa.yaml
    kubectl apply -f k8s/fastapi-pdb.yaml
    
    echo -e "${GREEN}✓ Application deployed${NC}\n"
}

# Wait for deployment
wait_for_deployment() {
    echo -e "${YELLOW}Waiting for deployment to be ready...${NC}"
    
    kubectl rollout status deployment/fastapi-app -n "$NAMESPACE" --timeout=300s
    
    echo -e "${GREEN}✓ Deployment is ready${NC}\n"
}

# Show deployment info
show_deployment_info() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Deployment Status${NC}"
    echo -e "${BLUE}========================================${NC}\n"
    
    echo -e "${YELLOW}Pods:${NC}"
    kubectl get pods -n "$NAMESPACE" -l app=fastapi-app
    
    echo -e "\n${YELLOW}Service:${NC}"
    kubectl get service fastapi-app -n "$NAMESPACE"
    
    echo -e "\n${YELLOW}Endpoints:${NC}"
    kubectl get endpoints fastapi-app -n "$NAMESPACE"
    
    # Get external IP if available
    EXTERNAL_IP=$(kubectl get service fastapi-app -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)
    if [ -n "$EXTERNAL_IP" ]; then
        echo -e "\n${GREEN}Application is accessible at: http://${EXTERNAL_IP}${NC}"
        echo -e "${GREEN}API Docs: http://${EXTERNAL_IP}/docs${NC}"
    else
        echo -e "\n${YELLOW}Waiting for LoadBalancer to get external IP...${NC}"
        echo "Run: kubectl get service fastapi-app -n $NAMESPACE"
    fi
    
    echo -e "\n${YELLOW}Recent Pod Logs:${NC}"
    kubectl logs -n "$NAMESPACE" -l app=fastapi-app --tail=10
}

# Main execution
main() {
    check_prerequisites
    build_image
    create_namespace
    deploy_application
    wait_for_deployment
    show_deployment_info
    
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo -e "${BLUE}========================================${NC}"
}

main "$@"
