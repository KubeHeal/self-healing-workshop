# Troubleshooting Option 1: Manual Deployment with Make Commands

This guide helps troubleshoot common issues when deploying the self-healing platform using **Option 1** (manual deployment via make commands from the `openshift-aiops-platform` repository).

## Prerequisites

Before running Option 1, ensure you have:

- OpenShift cluster access (4.18+ required)
- Logged into OpenShift: `oc whoami` should return your username
- Cloned the platform repository: `https://github.com/KubeHeal/openshift-aiops-platform.git`
- Required CLI tools: `oc`, `make`, `helm`, `yq`

## Common Issues

### Issue 1: `yq: Permission denied`

**Error Message**:
```
make: yq: Permission denied
Makefile:4: *** Pattern name MUST be set in values-global.yaml with the value .global.pattern.  Stop.
```

**Root Cause**: The bundled `yq` binary doesn't have execute permissions.

**Solution**:

```bash
# Navigate to the openshift-aiops-platform repository
cd ~/openshift-aiops-platform  # or your clone location

# Add execute permissions to yq
chmod +x yq

# Verify yq is executable
ls -la yq
# Should show: -rwxr-xr-x ... yq

# Test yq works
./yq --version

# Retry make command
make check-prerequisites
```

**Alternative Solutions**:

Option A - Install system-wide yq:
```bash
# RHEL/Fedora
sudo dnf install yq

# Or manual download (latest version)
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /tmp/yq
chmod +x /tmp/yq
sudo mv /tmp/yq /usr/local/bin/yq

# Verify installation
yq --version
```

Option B - Use podman/docker to run yq:
```bash
# Create yq alias using podman
alias yq='podman run --rm -i -v "${PWD}:/workdir" mikefarah/yq'

# Or add to ~/.bashrc for persistence
echo 'alias yq="podman run --rm -i -v \"\${PWD}:/workdir\" mikefarah/yq"' >> ~/.bashrc
source ~/.bashrc
```

### Issue 2: `Pattern name MUST be set in values-global.yaml`

**Error Message**:
```
Makefile:4: *** Pattern name MUST be set in values-global.yaml with the value .global.pattern.  Stop.
```

**Root Cause**: The `values-global.yaml` file is missing or doesn't have the required `.global.pattern` value.

**Solution**:

```bash
# Check if values-global.yaml exists
ls -la values-global.yaml

# If missing, create from the example template
cp values-global-example.yaml values-global.yaml

# Or manually create values-global.yaml with minimum required content:
cat > values-global.yaml <<EOF
global:
  pattern: self-healing-platform
  targetRevision: main
  namespace: self-healing-platform
EOF

# Verify the pattern is set correctly
yq eval '.global.pattern' values-global.yaml
# Should output: self-healing-platform
```

### Issue 3: `make check-prerequisites` fails with missing tools

**Error Message**:
```
Error: oc not found
Error: helm not found
```

**Solution**:

Install missing prerequisites:

```bash
# Install OpenShift CLI (oc)
# Option A - Download from Red Hat
curl -LO https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux.tar.gz
tar -xzf openshift-client-linux.tar.gz
sudo mv oc /usr/local/bin/
sudo chmod +x /usr/local/bin/oc

# Option B - Use package manager (if available)
sudo dnf install openshift-clients  # RHEL/Fedora

# Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installations
oc version
helm version
```

### Issue 4: Authentication failed when running make commands

**Error Message**:
```
Error: You must be logged in to the server (Unauthorized)
```

**Solution**:

```bash
# Log into OpenShift cluster
oc login <cluster-api-url> --token=<your-token>

# Or with username/password
oc login <cluster-api-url> -u <username> -p <password>

# Verify login
oc whoami
oc cluster-info

# Check you have cluster-admin permissions (required for platform deployment)
oc auth can-i create namespaces
# Should return: yes
```

### Issue 5: Validated Patterns Operator installation fails

**Error Message**:
```
Error: Failed to install validated-patterns-operator
```

**Solution**:

```bash
# Check if operator is already installed
oc get csv -n openshift-operators | grep validated-patterns

# If missing, manually install the operator
cat <<EOF | oc apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-operators
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: validated-patterns-operator
  namespace: openshift-operators
spec:
  channel: stable
  installPlanApproval: Automatic
  name: validated-patterns-operator
  source: community-operators
  sourceNamespace: openshift-marketplace
EOF

# Wait for operator to be ready
oc wait --for=condition=Ready pod -l app.kubernetes.io/name=validated-patterns-operator -n openshift-operators --timeout=300s
```

### Issue 6: Helm dependency update fails

**Error Message**:
```
Error: Failed to download dependencies for chart
```

**Solution**:

```bash
# Navigate to the chart directory
cd charts/self-healing-platform

# Manually update Helm dependencies
helm dependency update

# If specific dependency fails, check Chart.yaml
cat Chart.yaml | grep -A 5 dependencies

# Verify Helm repositories are added
helm repo list

# Add missing repositories if needed
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Retry
helm dependency update
```

### Issue 7: ArgoCD Application stuck in "Progressing" state

**Error Message**:
```
ArgoCD Application: Sync=Synced, Health=Progressing
```

**Solution**:

```bash
# Check ArgoCD Application status
oc get application self-healing-platform -n openshift-gitops -o yaml

# Check if resources are being created
oc get all -n self-healing-platform

# Force sync the application
oc patch application self-healing-platform -n openshift-gitops \
  --type merge -p '{"operation": {"initiatedBy": {"username": "admin"}, "sync": {"syncStrategy": {"hook": {}}}}}'

# Or use ArgoCD CLI
argocd app sync self-healing-platform

# Check ArgoCD server logs
oc logs -n openshift-gitops -l app.kubernetes.io/name=openshift-gitops-server --tail=50
```

### Issue 8: Namespace quota or resource limits exceeded

**Error Message**:
```
Error: exceeded quota
Error: insufficient resources
```

**Solution**:

```bash
# Check namespace resource quota
oc get resourcequota -n self-healing-platform
oc describe resourcequota -n self-healing-platform

# Check node resources
oc get nodes
oc describe node <node-name>

# If quotas are blocking deployment, request increase or clean up resources
oc delete pod <old-pod> -n self-healing-platform

# Check for PVCs that may be using storage
oc get pvc -n self-healing-platform
```

## Red Hat Credentials and Subscriptions

Some Ansible Automation Platform components may require Red Hat credentials:

**Ansible Automation Hub Token** (for execution environment images):

1. Go to: https://console.redhat.com/ansible/automation-hub/token
2. Copy your API token
3. Create secret in OpenShift:
   ```bash
   oc create secret docker-registry ansible-hub-registry \
     --docker-server=console.redhat.com \
     --docker-username=<your-username> \
     --docker-password=<your-token> \
     -n self-healing-platform
   ```

**Note**: The pre-built execution environment at `quay.io/takinosh/openshift-aiops-platform-ee:latest` is publicly available and doesn't require credentials.

## Validation

After resolving issues, validate the deployment:

```bash
# Run validation script from self-healing-workshop repository
cd /path/to/self-healing-workshop
./scripts/validate-workshop.sh

# Or manually check key resources
oc get all -n self-healing-platform
oc get inferenceservice -n self-healing-platform
oc get application self-healing-platform -n openshift-gitops
```

## Getting Help

If issues persist:

1. Check platform repository issues: https://github.com/KubeHeal/openshift-aiops-platform/issues
2. Review deployment logs:
   ```bash
   oc logs -n self-healing-platform -l app.kubernetes.io/part-of=self-healing-platform
   ```
3. Check ArgoCD for sync errors:
   ```bash
   oc describe application self-healing-platform -n openshift-gitops
   ```
4. Review this workshop repository issues: https://github.com/KubeHeal/self-healing-workshop/issues

## Next Steps

Once Option 1 deployment is successful:

1. Verify platform components are running: `./scripts/validate-workshop.sh`
2. Deploy workshop documentation: `./scripts/deploy-workshop-docs.sh`
3. Proceed to **Module 2** to configure OpenShift Lightspeed (create LLM secret and OLSConfig)
