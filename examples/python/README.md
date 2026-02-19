# OpenShift Lightspeed Python Examples

Ready-to-run Python scripts for integrating with OpenShift Lightspeed from the **Self-Healing Workshop Module 2**.

## Overview

These scripts demonstrate how to programmatically interact with OpenShift Lightspeed for cluster management, monitoring, and AI-powered operations.

## Prerequisites

- **Python 3.9+** installed
- Access to an OpenShift cluster with Lightspeed configured
- Network access to the Lightspeed server

## Quick Start

**Run the pre-built container with all scripts and dependencies included:**

```bash
# Run an interactive container
oc run lightspeed-examples \
  --image=image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-python-examples:latest \
  -n self-healing-platform \
  --rm -it -- bash

# Inside the container, all scripts are ready to use:
python lightspeed_client.py --help
python monitor_cluster.py
python pattern_alert_response.py
```

**Or run a specific script directly:**

```bash
# Run the monitoring script
oc run lightspeed-monitor \
  --image=image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-python-examples:latest \
  -n self-healing-platform \
  --rm -it -- python monitor_cluster.py

# Run with custom parameters
oc run lightspeed-monitor \
  --image=image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-python-examples:latest \
  -n self-healing-platform \
  --env="NAMESPACE=my-namespace" \
  --rm -it -- python monitor_cluster.py --interval 30
```

## Scripts

### Core Library

- **`lightspeed_client.py`** - Reusable LightspeedClient class for API interaction
  - `query()` - Send natural language queries
  - `get_recommendations()` - Get AI recommendations for issues

### Integration Patterns

- **`pattern_alert_response.py`** - Automated alert response system
  - Process Prometheus alerts
  - Query Lightspeed for analysis
  - Auto-remediate or escalate based on confidence

- **`pattern_batch_analysis.py`** - Batch pod fleet analysis
  - Analyze all pods in a namespace
  - Identify problematic pods
  - Generate CSV-style reports

- **`pattern_capacity_planning.py`** - Capacity planning report generator
  - Current resource usage
  - Time-based predictions
  - Capacity recommendations

### Monitoring

- **`monitor_cluster.py`** - Continuous cluster health monitor
  - Periodic health checks via Lightspeed
  - Console-based status updates
  - Configurable check intervals

## Usage Examples

### Query Lightspeed

```python
from lightspeed_client import LightspeedClient

client = LightspeedClient('http://ols-server:8000')
response = client.query(
    "What is the cluster health?",
    context={'namespace': 'self-healing-platform'}
)
print(response)
```

### Get Recommendations

```python
recommendations = client.get_recommendations(
    'high_resource_usage',
    {
        'pod_name': 'coordination-engine-0',
        'namespace': 'self-healing-platform',
        'cpu_usage': 85
    }
)
```

### Monitor Cluster Health

```bash
# Set environment variables
export OLS_SERVER_URL="http://ols-server:8000"
export NAMESPACE="self-healing-platform"

# Run monitor (checks every 60 seconds)
python monitor_cluster.py
```

## Testing

### Run Integration Tests

Test all scripts against your OpenShift Lightspeed instance:

```bash
# Using the wrapper script (recommended)
./scripts/test-python-examples.sh

# Or manually in the container
oc run python-test \
  --image=image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-python-examples:latest \
  -n self-healing-platform \
  --rm -it -- python test_integration.py
```

**What gets tested:**
- Lightspeed service connectivity
- All script imports and dependencies
- Command-line help flags
- Actual query execution against Lightspeed

**Expected output:**
```
==================================================
Lightspeed Python Examples - Integration Test Suite
==================================================

Testing: Lightspeed connectivity
Server URL: http://lightspeed-app-server.openshift-lightspeed.svc:8080
Status code: 200
✅ PASSED

Testing: lightspeed_client.py query
✓ Client created
✓ Query sent
Response keys: ['answer', 'confidence', 'sources']
✅ PASSED

TEST SUMMARY
Passed: 9
Failed: 0
Total:  9
```

## Running as Jobs and CronJobs

You can also run scripts as Kubernetes Jobs or CronJobs for automation:

### Method 1: Job for One-Time Execution

```bash
# Create a Job that runs the monitoring script
cat <<EOF | oc apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: lightspeed-monitor
  namespace: self-healing-platform
spec:
  template:
    spec:
      containers:
      - name: monitor
        image: image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-python-examples:latest
        command: ["python", "monitor_cluster.py", "--interval", "30"]
      restartPolicy: Never
  backoffLimit: 1
EOF

# View logs
oc logs -f job/lightspeed-monitor -n self-healing-platform
```

### Method 2: CronJob for Scheduled Execution

```bash
cat <<EOF | oc apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: capacity-planning
  namespace: self-healing-platform
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: report
            image: image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-python-examples:latest
            command: ["python", "pattern_capacity_planning.py", "--output", "/tmp/report.json"]
          restartPolicy: OnFailure
EOF
```

## Configuration

All scripts support environment variable configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLS_SERVER_URL` | Lightspeed server URL | `http://ols-server:8000` |
| `NAMESPACE` | Target namespace | `self-healing-platform` |
| `CHECK_INTERVAL` | Monitor check interval (seconds) | `60` |
| `TIMEOUT` | Request timeout (seconds) | `30` |

## Command-Line Arguments

Most scripts support command-line arguments. Use `--help` for details:

```bash
python lightspeed_client.py --help
python pattern_alert_response.py --help
python pattern_batch_analysis.py --help
```

## Troubleshooting

### Container Image Not Found

```
Error: ImagePullBackOff or ErrImagePull
```

**Cause:** The container image hasn't been built yet or doesn't exist in the registry.

**Solution:** Check if the image exists and trigger a build if needed:

```bash
# Check if ImageStream exists
oc get imagestream lightspeed-python-examples -n self-healing-platform

# Check if build completed
oc get builds -n self-healing-platform | grep lightspeed-python-examples

# Trigger a new build if needed
oc start-build lightspeed-python-examples -n self-healing-platform --wait
```

### Connection Refused

```
Error: Connection refused to http://lightspeed-app-server:8080
```

**Cause:** The Lightspeed service is not running or not accessible.

**Solution:** Verify the Lightspeed service is running:

```bash
# Check Lightspeed pods
oc get pods -n openshift-lightspeed

# Check service exists
oc get service lightspeed-app-server -n openshift-lightspeed

# Get service endpoint
oc get endpoints lightspeed-app-server -n openshift-lightspeed
```

### Script Errors

If scripts fail with errors, check the container logs:

```bash
# Run container with bash to debug
oc run lightspeed-debug \
  --image=image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-python-examples:latest \
  -n self-healing-platform \
  --rm -it -- bash

# Inside container, test individual components
python -c "import requests; print('requests OK')"
python -c "import pandas; print('pandas OK')"
python lightspeed_client.py --help
```

### Authentication Errors

These scripts connect to the internal Lightspeed server, which doesn't require authentication. If you're connecting to an external Lightspeed instance, you may need to add authentication headers.

## Advanced: Build Your Own Container

If you want to modify the scripts and build your own container:

```bash
# Clone the repository
git clone https://github.com/KubeHeal/self-healing-workshop.git
cd self-healing-workshop/examples/python

# Build with Docker/Podman
podman build -t lightspeed-examples:custom -f Containerfile .

# Push to OpenShift internal registry
podman tag lightspeed-examples:custom image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-examples:custom
podman push image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-examples:custom

# Or use OpenShift BuildConfig
oc apply -f openshift/imagestream.yaml
oc apply -f openshift/buildconfig.yaml
oc start-build lightspeed-python-examples --wait

# Run your custom container
oc run lightspeed-examples \
  --image=image-registry.openshift-image-registry.svc:5000/self-healing-platform/lightspeed-python-examples:latest \
  -n self-healing-platform \
  --rm -it -- bash
```

## Workshop Documentation

For complete context and step-by-step instructions, see:

- [Module 2: Deploy MCP Server & Configure Lightspeed](https://kubeheal.github.io/self-healing-workshop/module-02.html)
- [Workshop Repository](https://github.com/KubeHeal/self-healing-workshop)

## Related Resources

- [OpenShift Lightspeed Documentation](https://docs.openshift.com/container-platform/latest/lightspeed/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Platform Repository](https://github.com/KubeHeal/openshift-aiops-platform)

## License

These examples are part of the OpenShift Self-Healing Workshop and are provided for educational purposes.
