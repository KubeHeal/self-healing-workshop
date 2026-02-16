#!/bin/bash
#
# Deploy workshop documentation to OpenShift using declarative manifests
# Requires: oc CLI, built documentation in www/ directory
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
NAMESPACE="workshop-docs"
MANIFESTS_DIR="${PROJECT_ROOT}/manifests/workshop-docs"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function: Display usage information
show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

Deploy workshop documentation to OpenShift cluster.

OPTIONS:
    --build         Build documentation before deploying
    --status        Show deployment status only (no deployment)
    --help          Display this help message

EXAMPLES:
    $0                    # Deploy from pre-built www/ directory
    $0 --build            # Build and deploy
    $0 --status           # Check deployment status

PREREQUISITES:
    - Logged into OpenShift cluster (oc login)
    - Built documentation in www/ directory (or use --build)

EOF
}

# Function: Check prerequisites
check_prerequisites() {
    echo -e "${GREEN}Checking prerequisites...${NC}"

    # Check oc CLI
    if ! command -v oc &> /dev/null; then
        echo -e "${RED}Error: oc CLI is required but not installed${NC}"
        exit 1
    fi

    # Check oc login
    if ! oc whoami &> /dev/null; then
        echo -e "${RED}Error: Not logged into OpenShift cluster${NC}"
        echo "Please run: oc login <cluster-url>"
        exit 1
    fi

    echo "Logged in as: $(oc whoami)"
    echo "Cluster: $(oc whoami --show-server)"
}

# Function: Build container image from www/ directory
build_container_image() {
    echo -e "\n${GREEN}Building container image...${NC}"

    if [ ! -d "${PROJECT_ROOT}/www" ]; then
        echo -e "${RED}Error: www/ directory not found${NC}"
        echo "Run: ./scripts/build-workshop-docs.sh"
        exit 1
    fi

    if [ ! -f "${PROJECT_ROOT}/www/index.html" ]; then
        echo -e "${RED}Error: www/index.html not found${NC}"
        echo "Run: ./scripts/build-workshop-docs.sh"
        exit 1
    fi

    # Start binary build from www/ directory
    echo "Starting binary build from www/ directory..."
    cd "${PROJECT_ROOT}"
    oc start-build workshop-docs \
        --from-dir=www \
        --follow \
        -n "${NAMESPACE}"

    if [ $? -ne 0 ]; then
        echo -e "${RED}Build failed${NC}"
        exit 1
    fi

    echo "Container image built successfully"
}

# Function: Apply Kubernetes manifests
apply_manifests() {
    echo -e "\n${GREEN}Applying manifests with Kustomize...${NC}"

    if [ ! -f "${MANIFESTS_DIR}/kustomization.yaml" ]; then
        echo -e "${RED}Error: Manifests not found in ${MANIFESTS_DIR}${NC}"
        exit 1
    fi

    # Change to project root and apply using Kustomize
    cd "${PROJECT_ROOT}"
    oc apply -k manifests/workshop-docs/

    echo "Manifests applied"
}

# Function: Wait for deployment to be ready
wait_for_ready() {
    echo -e "\n${GREEN}Waiting for deployment...${NC}"

    if ! oc wait --for=condition=Available \
        deployment/workshop-docs \
        -n "${NAMESPACE}" \
        --timeout=120s 2>/dev/null; then
        echo -e "${YELLOW}Warning: Deployment not ready after 120s${NC}"
        echo "Check status with: oc get pods -n ${NAMESPACE}"
    else
        echo "Deployment ready"
    fi
}

# Function: Show deployment status
show_status() {
    echo -e "\n${GREEN}Deployment Status:${NC}"
    echo "===================="

    # Check namespace
    if ! oc get namespace "${NAMESPACE}" &> /dev/null; then
        echo -e "${RED}Namespace '${NAMESPACE}' not found${NC}"
        echo "Run deployment first: $0"
        return 1
    fi

    # Show resources
    echo -e "\n${YELLOW}Resources:${NC}"
    oc get all -n "${NAMESPACE}"

    # Show ConfigMaps
    echo -e "\n${YELLOW}ConfigMaps:${NC}"
    oc get configmap -n "${NAMESPACE}"

    # Get route URL
    if oc get route workshop-docs -n "${NAMESPACE}" &> /dev/null; then
        WORKSHOP_URL=$(oc get route workshop-docs -n "${NAMESPACE}" -o jsonpath='{.spec.host}')
        echo -e "\n${GREEN}Workshop URL:${NC}"
        echo "  https://${WORKSHOP_URL}"

        # Test HTTPS response
        echo -e "\n${YELLOW}Testing HTTPS response...${NC}"
        if curl -sI "https://${WORKSHOP_URL}" | grep -q "200 OK"; then
            echo -e "${GREEN}✓${NC} Workshop is accessible (HTTPS)"
        else
            echo -e "${YELLOW}⚠${NC} Workshop may not be accessible yet"
        fi

        # Test HTTP redirect
        if curl -sI "http://${WORKSHOP_URL}" | grep -q "302 Found"; then
            echo -e "${GREEN}✓${NC} HTTP redirects to HTTPS"
        fi
    else
        echo -e "${YELLOW}Route not found${NC}"
    fi
}

# Main execution
main() {
    local build_first=false
    local status_only=false

    # Parse command-line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                build_first=true
                shift
                ;;
            --status)
                status_only=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                echo -e "${RED}Unknown option: $1${NC}"
                show_usage
                exit 1
                ;;
        esac
    done

    # Status-only mode
    if [ "$status_only" = true ]; then
        check_prerequisites
        show_status
        exit 0
    fi

    # Build documentation if requested
    if [ "$build_first" = true ]; then
        echo -e "${GREEN}Building documentation...${NC}"
        "${SCRIPT_DIR}/build-workshop-docs.sh"
    fi

    # Deployment workflow
    check_prerequisites
    apply_manifests
    build_container_image
    wait_for_ready
    show_status

    echo -e "\n${GREEN}Deployment complete!${NC}"
}

# Run main function
main "$@"
