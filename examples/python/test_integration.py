#!/usr/bin/env python3
"""
Integration test suite for Lightspeed Python examples.
Tests scripts against actual OpenShift Lightspeed service.

Designed to run INSIDE the lightspeed-python-examples container.
"""

import os
import sys
import subprocess
import requests
from datetime import datetime

# Service configuration
OLS_SERVER_URL = os.getenv('OLS_SERVER_URL', 'http://lightspeed-app-server.openshift-lightspeed.svc:8080')
NAMESPACE = os.getenv('NAMESPACE', 'self-healing-platform')

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def test(self, name, fn):
        """Run a test and record result"""
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"{'='*60}")
        try:
            fn()
            print(f"✅ PASSED")
            self.passed += 1
            self.results.append((name, True, ""))
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            self.failed += 1
            self.results.append((name, False, str(e)))
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.failed += 1
            self.results.append((name, False, str(e)))

    def report(self):
        """Print summary report"""
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        print(f"{'='*60}\n")

        if self.failed > 0:
            print("Failed tests:")
            for name, passed, error in self.results:
                if not passed:
                    print(f"  ❌ {name}: {error}")

        return self.failed == 0

def test_lightspeed_connectivity():
    """Test 1: Verify Lightspeed service is reachable"""
    print(f"Server URL: {OLS_SERVER_URL}")

    # Try to connect (disable SSL verification for self-signed certs)
    try:
        response = requests.get(f"{OLS_SERVER_URL}/health", timeout=5, verify=False)
        print(f"Status code: {response.status_code}")
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
    except requests.exceptions.ConnectionError:
        raise AssertionError(f"Cannot connect to {OLS_SERVER_URL}")
    except requests.exceptions.Timeout:
        raise AssertionError(f"Timeout connecting to {OLS_SERVER_URL}")

def test_lightspeed_client_import():
    """Test 2: lightspeed_client.py imports successfully"""
    import lightspeed_client
    assert hasattr(lightspeed_client, 'LightspeedClient'), "Missing LightspeedClient class"
    print("✓ Module imported")
    print("✓ LightspeedClient class found")

def test_lightspeed_client_help():
    """Test 3: lightspeed_client.py --help works"""
    result = subprocess.run(
        ['python', 'lightspeed_client.py', '--help'],
        capture_output=True,
        text=True,
        timeout=5
    )
    assert result.returncode == 0, f"Exit code: {result.returncode}"
    assert 'usage:' in result.stdout.lower(), "No usage info in help"
    print(f"✓ Help output:\n{result.stdout[:200]}...")

def test_lightspeed_client_query():
    """Test 4: lightspeed_client.py can query Lightspeed"""
    from lightspeed_client import LightspeedClient

    client = LightspeedClient(OLS_SERVER_URL)
    print(f"✓ Client created: {OLS_SERVER_URL}")

    # Try a simple query
    response = client.query("What is the cluster health?", {"namespace": NAMESPACE})
    print(f"✓ Query sent")
    print(f"Response keys: {list(response.keys())}")

    # Check response structure
    assert 'error' not in response or response.get('answer'), \
        f"Query failed: {response.get('error', 'Unknown error')}"

def test_monitor_cluster_help():
    """Test 5: monitor_cluster.py --help works"""
    result = subprocess.run(
        ['python', 'monitor_cluster.py', '--help'],
        capture_output=True,
        text=True,
        timeout=5
    )
    assert result.returncode == 0, f"Exit code: {result.returncode}"
    assert 'usage:' in result.stdout.lower(), "No usage info"
    print("✓ Help works")

def test_pattern_alert_response_help():
    """Test 6: pattern_alert_response.py --help works"""
    result = subprocess.run(
        ['python', 'pattern_alert_response.py', '--help'],
        capture_output=True,
        text=True,
        timeout=5
    )
    assert result.returncode == 0, f"Exit code: {result.returncode}"
    assert 'usage:' in result.stdout.lower(), "No usage info"
    print("✓ Help works")

def test_pattern_batch_analysis_help():
    """Test 7: pattern_batch_analysis.py --help works"""
    result = subprocess.run(
        ['python', 'pattern_batch_analysis.py', '--help'],
        capture_output=True,
        text=True,
        timeout=5
    )
    assert result.returncode == 0, f"Exit code: {result.returncode}"
    assert 'usage:' in result.stdout.lower(), "No usage info"
    print("✓ Help works")

def test_pattern_capacity_planning_help():
    """Test 8: pattern_capacity_planning.py --help works"""
    result = subprocess.run(
        ['python', 'pattern_capacity_planning.py', '--help'],
        capture_output=True,
        text=True,
        timeout=5
    )
    assert result.returncode == 0, f"Exit code: {result.returncode}"
    assert 'usage:' in result.stdout.lower(), "No usage info"
    print("✓ Help works")

def test_dependencies():
    """Test 9: All dependencies are installed"""
    import requests
    print("✓ requests installed")

    import pandas
    print("✓ pandas installed")

def main():
    print("\n" + "="*60)
    print("Lightspeed Python Examples - Integration Test Suite")
    print("="*60)
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Server: {OLS_SERVER_URL}")
    print(f"Namespace: {NAMESPACE}")
    print("="*60)

    runner = TestRunner()

    # Basic tests
    runner.test("Dependencies installed", test_dependencies)
    runner.test("Lightspeed connectivity", test_lightspeed_connectivity)

    # Script import tests
    runner.test("lightspeed_client.py imports", test_lightspeed_client_import)

    # CLI help tests
    runner.test("lightspeed_client.py --help", test_lightspeed_client_help)
    runner.test("monitor_cluster.py --help", test_monitor_cluster_help)
    runner.test("pattern_alert_response.py --help", test_pattern_alert_response_help)
    runner.test("pattern_batch_analysis.py --help", test_pattern_batch_analysis_help)
    runner.test("pattern_capacity_planning.py --help", test_pattern_capacity_planning_help)

    # Integration test (requires working Lightspeed)
    runner.test("lightspeed_client.py query", test_lightspeed_client_query)

    # Print summary
    success = runner.report()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
