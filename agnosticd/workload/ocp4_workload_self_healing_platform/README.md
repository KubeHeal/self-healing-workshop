# ocp4_workload_self_healing_platform

AgnosticD V2 workload to deploy the OpenShift AI Ops Self-Healing Platform for workshop environments.

## Overview

This workload deploys the complete Self-Healing Platform including:

- **Validated Patterns Operator** - GitOps-based deployment
- **Coordination Engine** - Go-based remediation orchestrator
- **MCP Server** - Model Context Protocol server for Lightspeed
- **KServe ML Models** - Anomaly detection and predictive analytics
- **OpenShift Lightspeed** (optional) - AI assistant integration
- **Jupyter Workbench** - ML development environment

## Requirements

- OpenShift 4.18+
- Cluster admin access
- Storage class available (ODF recommended)

## Execution Environment

This workload uses a **pre-built execution environment** image that contains all required Ansible collections and dependencies:

```
quay.io/takinosh/openshift-aiops-platform-ee:latest
```

The image is automatically built by GitHub Actions when the EE definition changes:
- **Source**: [openshift-aiops-platform](https://github.com/KubeHeal/openshift-aiops-platform)
- **Workflow**: `.github/workflows/build-ee.yml`

**Benefits**:
- No Ansible Hub token required
- Faster deployments (pre-built image)
- Consistent environment across deployments

## Usage

### Variables File

Create a variables file in `agnosticd-v2-vars/`:

```yaml
# self-healing-workshop.yml
---
cloud_provider: none
config: openshift-workloads

requirements_content:
  collections:
  - name: https://github.com/KubeHeal/self-healing-workshop.git
    type: git
    version: main

clusters:
- default:
    api_url: "{{ cluster1.sandbox_openshift_api_url }}"
    api_token: "{{ cluster1.sandbox_openshift_api_token }}"

workloads:
- kubeheal.self_healing_workshop.ocp4_workload_self_healing_platform

# Platform configuration
self_healing_platform_git_repo: "https://github.com/KubeHeal/openshift-aiops-platform.git"
self_healing_platform_git_ref: "main"
self_healing_platform_namespace: "self-healing-platform"
self_healing_platform_deploy_lightspeed: true
self_healing_platform_llm_provider: "openai"
```

### Deploy

```bash
cd ~/agnosticd-v2
./bin/agd provision -g workshop1 -c self-healing-workshop -a sandbox1234
```

### Destroy

```bash
./bin/agd destroy -g workshop1 -c self-healing-workshop -a sandbox1234
```

## Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `self_healing_platform_ee_image` | `quay.io/takinosh/openshift-aiops-platform-ee:latest` | Pre-built execution environment image |
| `self_healing_platform_namespace` | `self-healing-platform` | Target namespace |
| `self_healing_platform_git_repo` | `https://github.com/KubeHeal/openshift-aiops-platform.git` | Platform repository |
| `self_healing_platform_git_ref` | `main` | Git branch/tag |
| `self_healing_platform_deploy_lightspeed` | `true` | Install Lightspeed operator |
| `self_healing_platform_llm_provider` | `openai` | LLM provider for Lightspeed |
| `self_healing_platform_deploy_workbench` | `true` | Deploy Jupyter workbench |
| `self_healing_platform_deploy_gpu_workloads` | `false` | Enable GPU workloads |

## Post-Deployment

After deployment, you need to:

1. **Create LLM API key secret** (if using Lightspeed):
   ```bash
   oc create secret generic openai-credentials \
     -n openshift-lightspeed \
     --from-literal=api_key='your-api-key'
   ```

2. **Create OLSConfig** (see workshop documentation)

3. **Access the workshop** via OpenShift console

## Troubleshooting

### Pods not starting

```bash
# Check pod status
oc get pods -n self-healing-platform

# Check events
oc get events -n self-healing-platform --sort-by='.lastTimestamp'
```

### ArgoCD sync issues

```bash
# Check ArgoCD application
oc get application self-healing-platform -n openshift-gitops -o yaml

# Sync manually
argocd app sync self-healing-platform
```

### Lightspeed not working

```bash
# Check OLSConfig
oc get olsconfig cluster -o yaml

# Check operator logs
oc logs -n openshift-lightspeed -l app=lightspeed-operator
```

## Resources

- [Self-Healing Workshop](https://github.com/KubeHeal/self-healing-workshop)
- [OpenShift AI Ops Platform](https://github.com/KubeHeal/openshift-aiops-platform)
- [AgnosticD V2](https://github.com/agnosticd/agnosticd-v2)

## License

GNU General Public License v3.0
