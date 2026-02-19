# OpenShift Lightspeed Python Examples

Ready-to-run Python scripts for integrating with OpenShift Lightspeed from the **Self-Healing Workshop Module 2**.

## Overview

These scripts demonstrate how to programmatically interact with OpenShift Lightspeed for cluster management, monitoring, and AI-powered operations.

## Prerequisites

- **Python 3.9+** installed
- Access to an OpenShift cluster with Lightspeed configured
- Network access to the Lightspeed server

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Lightspeed server URL (adjust based on your deployment)
export OLS_SERVER_URL="http://ols-server:8000"

# Target namespace for cluster operations
export NAMESPACE="self-healing-platform"
```

### 3. Run Examples

```bash
# Test the LightspeedClient library
python lightspeed_client.py

# Test integration patterns
python pattern_alert_response.py
python pattern_batch_analysis.py
python pattern_capacity_planning.py

# Run the monitoring script
python monitor_cluster.py
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

## Running in OpenShift

You can run these scripts inside OpenShift pods:

```bash
# Create a pod with Python
oc run python-client --image=python:3.11 --rm -it -- bash

# Inside the pod:
curl -O https://raw.githubusercontent.com/KubeHeal/self-healing-workshop/main/examples/python/lightspeed_client.py
curl -O https://raw.githubusercontent.com/KubeHeal/self-healing-workshop/main/examples/python/requirements.txt
pip install -r requirements.txt

# Set environment variables
export OLS_SERVER_URL="http://ols-server.openshift-lightspeed.svc:8000"
export NAMESPACE="self-healing-platform"

# Run scripts
python lightspeed_client.py
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

### Connection Refused

```
Error: Connection refused to http://ols-server:8000
```

**Solution:** Verify Lightspeed server is running and accessible:

```bash
oc get pods -n openshift-lightspeed
oc get service ols-server -n openshift-lightspeed
```

If running outside the cluster, use port-forward:

```bash
oc port-forward -n openshift-lightspeed svc/ols-server 8000:8000
```

### Module Not Found

```
ModuleNotFoundError: No module named 'requests'
```

**Solution:** Install dependencies:

```bash
pip install -r requirements.txt
```

### Authentication Errors

These scripts connect to the internal Lightspeed server, which doesn't require authentication. If you're connecting to an external Lightspeed instance, you may need to add authentication headers.

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
