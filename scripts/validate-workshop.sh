#!/bin/bash
# Validate Self-Healing Workshop deployment
# Usage: ./scripts/validate-workshop.sh [namespace]

set -e

NAMESPACE="${1:-self-healing-platform}"
ERRORS=0

echo "=========================================="
echo "Self-Healing Workshop Validation"
echo "Namespace: ${NAMESPACE}"
echo "=========================================="
echo ""

# Check if oc is available
if ! command -v oc &> /dev/null; then
    echo "❌ oc CLI not found"
    exit 1
fi

# Check cluster access
echo "Checking cluster access..."
if ! oc whoami &> /dev/null; then
    echo "❌ Not logged into OpenShift cluster"
    exit 1
fi
echo "✅ Cluster access OK ($(oc whoami))"
echo ""

# Check namespace exists
echo "Checking namespace..."
if ! oc get namespace "${NAMESPACE}" &> /dev/null; then
    echo "❌ Namespace ${NAMESPACE} not found"
    ((ERRORS++))
else
    echo "✅ Namespace ${NAMESPACE} exists"
fi
echo ""

# Check core deployments
echo "Checking core deployments..."
DEPLOYMENTS=("coordination-engine" "mcp-server")
for dep in "${DEPLOYMENTS[@]}"; do
    READY=$(oc get deployment "${dep}" -n "${NAMESPACE}" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
    if [[ "${READY}" -gt 0 ]]; then
        echo "✅ ${dep}: ${READY} replicas ready"
    else
        echo "❌ ${dep}: not ready"
        ((ERRORS++))
    fi
done
echo ""

# Check InferenceServices
echo "Checking ML models (InferenceServices)..."
MODELS=("anomaly-detector" "predictive-analytics")
for model in "${MODELS[@]}"; do
    STATUS=$(oc get inferenceservice "${model}" -n "${NAMESPACE}" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "Unknown")
    if [[ "${STATUS}" == "True" ]]; then
        echo "✅ ${model}: Ready"
    else
        echo "⚠️  ${model}: ${STATUS} (may still be deploying)"
    fi
done
echo ""

# Check OpenShift Lightspeed
echo "Checking OpenShift Lightspeed..."
if oc get olsconfig cluster &> /dev/null; then
    STATUS=$(oc get olsconfig cluster -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "Unknown")
    echo "✅ OLSConfig exists (Available: ${STATUS})"
else
    echo "⚠️  OLSConfig not configured (Lightspeed may not work)"
fi
echo ""

# Check ArgoCD Application
echo "Checking ArgoCD Application..."
if oc get application self-healing-platform -n openshift-gitops &> /dev/null; then
    SYNC=$(oc get application self-healing-platform -n openshift-gitops -o jsonpath='{.status.sync.status}' 2>/dev/null || echo "Unknown")
    HEALTH=$(oc get application self-healing-platform -n openshift-gitops -o jsonpath='{.status.health.status}' 2>/dev/null || echo "Unknown")
    echo "✅ ArgoCD Application: Sync=${SYNC}, Health=${HEALTH}"
else
    echo "⚠️  ArgoCD Application not found"
fi
echo ""

# Check Jupyter workbench
echo "Checking Jupyter Workbench..."
if oc get statefulset self-healing-workbench -n "${NAMESPACE}" &> /dev/null; then
    READY=$(oc get statefulset self-healing-workbench -n "${NAMESPACE}" -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
    echo "✅ Jupyter Workbench: ${READY} replicas ready"
else
    echo "⚠️  Jupyter Workbench not deployed"
fi
echo ""

# Summary
echo "=========================================="
if [[ ${ERRORS} -eq 0 ]]; then
    echo "✅ Validation PASSED"
    echo ""
    echo "Workshop is ready! Access:"
    echo "- OpenShift Console: $(oc get console cluster -o jsonpath='{.status.consoleURL}' 2>/dev/null || echo 'N/A')"
    echo "- Click Lightspeed icon (✨) to start chatting"
else
    echo "❌ Validation FAILED (${ERRORS} errors)"
    echo ""
    echo "Check deployment logs:"
    echo "  oc logs -n ${NAMESPACE} -l app.kubernetes.io/part-of=self-healing-platform"
fi
echo "=========================================="

exit ${ERRORS}
