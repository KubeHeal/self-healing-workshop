# Workshop Documentation Deployment Manifests

This directory contains declarative Kubernetes manifests for deploying the Self-Healing Workshop documentation to an OpenShift cluster.

## Architecture

The deployment consists of:

- **Namespace**: `workshop-docs` - Isolated namespace for documentation resources
- **ConfigMap**: `workshop-info` - Workshop metadata (name, repository URLs, etc.)
- **ConfigMap**: `workshop-docs-content` - Built Antora documentation (HTML/CSS/JS files)
- **Deployment**: `workshop-docs` - nginx web server serving static content
- **Service**: `workshop-docs` - ClusterIP service exposing port 8080
- **Route**: `workshop-docs` - OpenShift Route for external HTTP access

## Prerequisites

1. **OpenShift cluster access**:
   ```bash
   oc login <cluster-url>
   oc whoami  # Verify login
   ```

2. **Built documentation**:
   ```bash
   cd /path/to/self-healing-workshop
   ./scripts/build-workshop-docs.sh
   # Verify: ls www/index.html
   ```

## Deployment Options

### Option 1: Automated Deployment (Recommended)

Use the deployment script for a complete, automated deployment:

```bash
# Build and deploy
./scripts/deploy-workshop-docs.sh --build

# Deploy from pre-built www/ directory
./scripts/deploy-workshop-docs.sh

# Check status
./scripts/deploy-workshop-docs.sh --status
```

### Option 2: Manual Deployment with Kustomize

Deploy using `oc apply -k` for a declarative, GitOps-friendly approach:

```bash
# 1. Create content ConfigMap from built documentation
oc create configmap workshop-docs-content \
  --from-file=www/ \
  -n workshop-docs \
  --dry-run=client -o yaml | oc apply -f -

# 2. Apply all manifests using Kustomize
oc apply -k manifests/workshop-docs/

# 3. Wait for deployment to be ready
oc wait --for=condition=Available \
  deployment/workshop-docs \
  -n workshop-docs \
  --timeout=120s

# 4. Get workshop URL
oc get route workshop-docs -n workshop-docs
```

### Option 3: Manual Deployment without Kustomize

Apply individual manifest files:

```bash
# Apply manifests in order
oc apply -f manifests/workshop-docs/namespace.yaml
oc apply -f manifests/workshop-docs/configmap.yaml
oc apply -f manifests/workshop-docs/deployment.yaml
oc apply -f manifests/workshop-docs/service.yaml
oc apply -f manifests/workshop-docs/route.yaml

# Create content ConfigMap
oc create configmap workshop-docs-content \
  --from-file=www/ \
  -n workshop-docs \
  --dry-run=client -o yaml | oc apply -f -
```

## Manifest Files

### namespace.yaml
Creates the `workshop-docs` namespace with proper labels:
- `workshop: self-healing`
- `app.kubernetes.io/part-of: self-healing-workshop`

### configmap.yaml
Workshop metadata ConfigMap with:
- Workshop name
- Platform namespace reference
- Repository URLs

### deployment.yaml
nginx deployment configuration:
- Uses UBI9 nginx image (`registry.access.redhat.com/ubi9/nginx-124:latest`)
- Mounts `workshop-docs-content` ConfigMap at `/opt/app-root/src`
- Resource limits: 128Mi memory, 100m CPU
- Liveness and readiness probes on port 8080

### service.yaml
ClusterIP Service exposing the nginx deployment:
- Port 8080 (HTTP)
- Selector: `app: workshop-docs`

### route.yaml
OpenShift Route for external access:
- HTTP (non-TLS) route
- Auto-generates hostname from cluster domain

### kustomization.yaml
Kustomize configuration orchestrating all manifests:
- Sets common namespace: `workshop-docs`
- Applies common labels
- Orders resource creation

## Updating Documentation

To update the workshop documentation after content changes:

```bash
# 1. Rebuild documentation
./scripts/build-workshop-docs.sh

# 2. Update content ConfigMap
oc create configmap workshop-docs-content \
  --from-file=www/ \
  -n workshop-docs \
  --dry-run=client -o yaml | oc apply -f -

# 3. Restart deployment to pick up changes
oc rollout restart deployment/workshop-docs -n workshop-docs

# 4. Wait for rollout to complete
oc rollout status deployment/workshop-docs -n workshop-docs
```

Or use the deployment script:

```bash
./scripts/deploy-workshop-docs.sh --build
```

## Verification

Check deployment status:

```bash
# All resources
oc get all -n workshop-docs

# Deployment status
oc get deployment workshop-docs -n workshop-docs

# Pod logs
oc logs -l app=workshop-docs -n workshop-docs

# Route URL
WORKSHOP_URL=$(oc get route workshop-docs -n workshop-docs -o jsonpath='{.spec.host}')
echo "Workshop URL: http://${WORKSHOP_URL}"

# Test HTTP response
curl -I http://${WORKSHOP_URL}
```

## Troubleshooting

### Deployment not ready

```bash
# Check pod status
oc get pods -n workshop-docs

# View pod logs
oc logs -l app=workshop-docs -n workshop-docs

# Describe deployment
oc describe deployment workshop-docs -n workshop-docs
```

### ConfigMap too large

If the ConfigMap exceeds size limits (>1MB), consider:
- Using S2I binary builds instead (see old deployment script)
- Using PersistentVolumeClaim instead of ConfigMap
- Hosting documentation externally (GitHub Pages, S3, etc.)

### Route not accessible

```bash
# Check route status
oc get route workshop-docs -n workshop-docs -o yaml

# Verify service endpoints
oc get endpoints workshop-docs -n workshop-docs

# Test from within cluster
oc run -it --rm debug --image=registry.access.redhat.com/ubi9/ubi-minimal:latest --restart=Never -- \
  curl -I http://workshop-docs.workshop-docs.svc:8080
```

## GitOps Integration

These manifests are GitOps-ready and can be managed by ArgoCD or similar tools:

```yaml
# ArgoCD Application example
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: workshop-docs
  namespace: openshift-gitops
spec:
  project: default
  source:
    repoURL: https://github.com/KubeHeal/self-healing-workshop
    targetRevision: main
    path: manifests/workshop-docs
  destination:
    server: https://kubernetes.default.svc
    namespace: workshop-docs
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

**Note**: The `workshop-docs-content` ConfigMap must be created manually or via a CI/CD pipeline, as it contains generated content from the build process.

## Clean Up

Remove all workshop documentation resources:

```bash
# Delete namespace (removes all resources)
oc delete namespace workshop-docs

# Or delete individual resources
oc delete -k manifests/workshop-docs/
```

## Related Documentation

- Build script: `scripts/build-workshop-docs.sh`
- Deployment script: `scripts/deploy-workshop-docs.sh`
- Main README: `README.md`
- Workshop content: `content/modules/ROOT/pages/`
