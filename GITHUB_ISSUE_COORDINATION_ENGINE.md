# GitHub Issue: Self-healing remediation should update deployment resources

**Repository:** https://github.com/KubeHeal/openshift-coordination-engine/issues

---

## Title

Self-healing remediation should update deployment resources, not just delete pods

## Labels

- `enhancement`
- `self-healing`
- `remediation`

## Body

### Problem

When Lightspeed triggers automated remediation for OOMKilled pods via the coordination-engine, it currently only **deletes and recreates pods** without addressing the root cause (insufficient resource limits).

### Current Behavior

1. User deploys broken-app with 96Mi memory limit
2. App OOMKills after ~7 requests due to memory leak
3. User asks Lightspeed: "Analyze broken-app pods for anomalies"
4. User asks: "Fix it automatically"
5. Coordination-engine response:
   ```
   Actions triggered:
   - Delete pod broken-app-xxx (workflow wf-abc)
   - Delete pod broken-app-yyy (workflow wf-def)
   ```
6. Pods recreate with **same 96Mi limit** → OOMKill recurs

### Expected Behavior

The coordination-engine should:

1. Detect OOMKilled pods are caused by insufficient memory limits (96Mi)
2. Calculate appropriate new limit (e.g., 256Mi = ~2.5x current limit)
3. Update the Deployment resource spec:
   ```yaml
   resources:
     limits:
       memory: 256Mi  # was 96Mi
   ```
4. Allow Deployment controller to roll out pods with new limits
5. Track remediation action in incident history

### Reproduction Steps

1. Deploy test app with low memory limit:
   ```bash
   oc apply -f - <<EOF
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: broken-app
     namespace: self-healing-platform
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: broken-app
     template:
       metadata:
         labels:
           app: broken-app
       spec:
         containers:
         - name: web
           image: registry.access.redhat.com/ubi9/python-311:latest
           command: ["/bin/bash", "-c"]
           args:
           - |
             pip install flask && python -c '
             from flask import Flask
             app = Flask(__name__)
             data = []
             @app.route("/")
             def hello():
                 data.append("x" * 1024 * 1024 * 10)  # 10MB per request
                 return f"Allocated {len(data)} chunks ({len(data) * 10}MB total)"
             app.run(host="0.0.0.0", port=8080)
             '
           ports:
           - containerPort: 8080
           resources:
             limits:
               memory: "96Mi"
               cpu: "100m"
             requests:
               memory: "64Mi"
               cpu: "50m"
   EOF
   ```

2. Trigger memory leak:
   ```bash
   for i in {1..20}; do
     oc exec -n self-healing-platform deployment/broken-app -- curl -s http://localhost:8080/
     sleep 1
   done
   ```

3. Verify OOMKilled: `oc get pods -n self-healing-platform -l app=broken-app`

4. In Lightspeed UI:
   - Query: "Analyze broken-app pods for anomalies"
   - Query: "Fix it automatically"

5. Observe: Pods deleted/recreated but deployment spec unchanged

### Proposed Solution

**Option 1: Patch Deployment Resources (Recommended)**

When `trigger-remediation` MCP tool detects OOMKilled:

```go
// Pseudo-code
if incident.Type == "OOMKilled" {
  currentLimit := deployment.Spec.Template.Spec.Containers[0].Resources.Limits.Memory
  newLimit := currentLimit * 2.5  // or use ML model prediction

  patch := []byte(`[
    {"op": "replace", "path": "/spec/template/spec/containers/0/resources/limits/memory", "value": "` + newLimit + `"}
  ]`)

  client.AppsV1().Deployments(namespace).Patch(ctx, deploymentName, types.JSONPatchType, patch, metav1.PatchOptions{})

  logIncident("Updated deployment memory limit", currentLimit, newLimit)
}
```

**Option 2: Use Deployment Annotations**

Add annotation to track remediation history:

```yaml
metadata:
  annotations:
    self-healing.kubeheal.io/last-remediation: "2026-02-20T15:30:00Z"
    self-healing.kubeheal.io/memory-increase: "96Mi->256Mi"
```

**Option 3: Create ConfigMap for Remediation Rules**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: remediation-rules
data:
  oomkilled-memory-multiplier: "2.5"
  oomkilled-max-limit: "1Gi"
  cpu-throttled-increase: "200m"
```

### Impact

**Severity:** High - Breaks core self-healing demo in workshop Module 3

**Workaround:** Users must manually patch deployment after Lightspeed remediation:

```bash
oc patch deployment broken-app -n self-healing-platform --type='json' -p='[
  {"op": "replace", "path": "/spec/template/spec/containers/0/resources/limits/memory", "value": "256Mi"}
]'
```

### Related

- Workshop Module 3: https://kubeheal.github.io/self-healing-workshop/modules/module-03.html
- MCP Server Tools: https://github.com/KubeHeal/openshift-cluster-health-mcp
- Anomaly Detection Model: https://github.com/KubeHeal/openshift-aiops-platform (notebooks/anomaly-detector)

### Environment

- OpenShift: 4.18+
- Coordination Engine: v0.1.x (check current version in deployment)
- MCP Server: Latest from platform deployment
- Lightspeed: Configured with OLSConfig

### Additional Context

This issue was discovered during workshop testing where users expect true self-healing (resource limit updates) but only get pod restarts. The current behavior provides partial value (service recovery via pod restart) but doesn't prevent recurrence of the root cause.

---

## Instructions for Submitting

1. Go to: https://github.com/KubeHeal/openshift-coordination-engine/issues/new
2. Copy the **Title** above
3. Copy the **Body** section above
4. Add labels: `enhancement`, `self-healing`, `remediation` (if you have permissions)
5. Submit the issue
6. Copy the issue URL and update Module 3 with the actual issue number

Once the issue is created, update the placeholders in Module 3:
- Search for: `https://github.com/KubeHeal/openshift-coordination-engine/issues/[planned]`
- Replace with: `https://github.com/KubeHeal/openshift-coordination-engine/issues/XXX` (actual issue number)
