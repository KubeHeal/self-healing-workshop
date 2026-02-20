#!/bin/bash
#
# Test Python examples in the lightspeed-python-examples container
# Runs integration tests against the actual cluster
#

set -e

NAMESPACE="${NAMESPACE:-self-healing-platform}"
IMAGE="image-registry.openshift-image-registry.svc:5000/${NAMESPACE}/lightspeed-python-examples:latest"

echo "=================================================="
echo "Python Examples Integration Test"
echo "=================================================="
echo "Namespace: ${NAMESPACE}"
echo "Image: ${IMAGE}"
echo "=================================================="
echo ""

# Check if image exists
if ! oc get imagestream lightspeed-python-examples -n "${NAMESPACE}" &>/dev/null; then
    echo "❌ ERROR: Container image not found"
    echo ""
    echo "Build the image first:"
    echo "  oc start-build lightspeed-python-examples -n ${NAMESPACE} --wait"
    exit 1
fi

# Run tests in ephemeral pod
echo "Running tests in container..."
echo ""

oc run python-integration-test \
    --image="${IMAGE}" \
    -n "${NAMESPACE}" \
    --rm -it \
    --restart=Never \
    --env="OLS_SERVER_URL=https://lightspeed-app-server.openshift-lightspeed.svc.cluster.local:8443" \
    -- python test_integration.py

echo ""
echo "=================================================="
echo "Test complete!"
echo "=================================================="
