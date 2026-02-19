#!/usr/bin/env python3
"""
Cluster Health Monitor with Lightspeed

Simple monitoring script that continuously checks cluster health using
OpenShift Lightspeed's natural language interface.

Workshop: OpenShift Self-Healing with Lightspeed - Module 2, Part 10
Source: https://github.com/KubeHeal/self-healing-workshop

Usage:
    python monitor_cluster.py
    python monitor_cluster.py --interval 30
    python monitor_cluster.py --server http://ols-server:8000 --namespace default
"""

import os
import sys
import argparse
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: requests library not installed")
    print("Install with: pip install requests")
    sys.exit(1)


def query_lightspeed(server_url: str, question: str, context: dict = None, timeout: int = 30) -> dict:
    """
    Send query to Lightspeed.

    Args:
        server_url: Lightspeed server URL
        question: Natural language question
        context: Optional context dictionary
        timeout: Request timeout in seconds

    Returns:
        Response dictionary or error dict
    """
    try:
        response = requests.post(
            f"{server_url}/query",
            json={'question': question, 'context': context or {}},
            timeout=timeout
        )
        return response.json() if response.ok else {'error': f"HTTP {response.status_code}: {response.text}"}
    except requests.exceptions.RequestException as e:
        return {'error': f"Request failed: {str(e)}"}
    except Exception as e:
        return {'error': f"Unexpected error: {str(e)}"}


def check_cluster_health(server_url: str, namespace: str) -> bool:
    """
    Check cluster health via Lightspeed.

    Args:
        server_url: Lightspeed server URL
        namespace: Namespace to check

    Returns:
        True if healthy, False otherwise
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking cluster health...")

    response = query_lightspeed(
        server_url,
        f"Are there any issues in the {namespace} namespace?",
        {'namespace': namespace}
    )

    if 'error' in response:
        print(f"  ⚠️  Error: {response['error']}")
        return False

    # Check for issues in response
    answer = response.get('answer', '').lower()
    if any(word in answer for word in ['healthy', 'no issues', 'running', 'normal']):
        print(f"  ✅ All systems healthy")
        print(f"     {response.get('answer', '')[:150]}")
        return True
    else:
        print(f"  ⚠️  Potential issues detected:")
        print(f"     {response.get('answer', 'Unknown')[:200]}")
        return False


def main():
    """Main monitoring loop."""
    parser = argparse.ArgumentParser(
        description='Continuous Cluster Health Monitor with Lightspeed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor with default settings (checks every 60 seconds)
  python monitor_cluster.py

  # Check every 30 seconds
  python monitor_cluster.py --interval 30

  # Monitor specific namespace
  python monitor_cluster.py --namespace my-namespace

  # Specify server URL and namespace
  python monitor_cluster.py --server http://ols-server:8000 --namespace default

Environment Variables:
  OLS_SERVER_URL    Lightspeed server URL
                    Inside cluster: http://lightspeed-app-server.openshift-lightspeed.svc:8080
                    Via port-forward: http://localhost:8080
  NAMESPACE         Namespace to monitor (default: self-healing-platform)
  CHECK_INTERVAL    Check interval in seconds (default: 60)

Press Ctrl+C to stop monitoring.
        """
    )

    parser.add_argument(
        '--server',
        default=os.getenv('OLS_SERVER_URL', 'http://lightspeed-app-server.openshift-lightspeed.svc:8080'),
        help='Lightspeed server URL'
    )

    parser.add_argument(
        '--namespace',
        default=os.getenv('NAMESPACE', 'self-healing-platform'),
        help='Namespace to monitor'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=int(os.getenv('CHECK_INTERVAL', '60')),
        help='Check interval in seconds (default: 60)'
    )

    args = parser.parse_args()

    # Print banner
    print("=" * 70)
    print("OpenShift Lightspeed Cluster Health Monitor")
    print("=" * 70)
    print(f"Server URL: {args.server}")
    print(f"Namespace: {args.namespace}")
    print(f"Check interval: {args.interval} seconds")
    print("=" * 70)
    print("\nPress Ctrl+C to stop monitoring\n")

    # Test connectivity first
    print("Testing connection to Lightspeed...")
    test_response = query_lightspeed(args.server, "Hello", {}, timeout=10)
    if 'error' in test_response:
        print(f"❌ Failed to connect: {test_response['error']}")
        print("\nTroubleshooting:")
        print("  1. Verify Lightspeed server is running:")
        print("     oc get pods -n openshift-lightspeed")
        print("  2. Check service endpoint:")
        print("     oc get svc -n openshift-lightspeed")
        print("  3. If running outside cluster, use port-forward:")
        print("     oc port-forward -n openshift-lightspeed svc/ols-server 8000:8000")
        sys.exit(1)
    else:
        print("✅ Connected successfully\n")

    # Main monitoring loop
    check_count = 0
    error_count = 0

    while True:
        try:
            check_count += 1
            healthy = check_cluster_health(args.server, args.namespace)

            if not healthy:
                error_count += 1

            # Print statistics periodically
            if check_count % 10 == 0:
                print(f"\n--- Statistics after {check_count} checks ---")
                print(f"Healthy checks: {check_count - error_count}")
                print(f"Issues detected: {error_count}")
                print(f"Success rate: {(check_count - error_count) / check_count * 100:.1f}%")
                print("-" * 40 + "\n")

            # Sleep until next check
            time.sleep(args.interval)

        except KeyboardInterrupt:
            print("\n\n" + "="*70)
            print("Monitoring stopped by user")
            print("="*70)
            print(f"Total checks: {check_count}")
            print(f"Issues detected: {error_count}")
            print(f"Success rate: {(check_count - error_count) / check_count * 100:.1f}%")
            print("="*70)
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            error_count += 1
            print("Continuing monitoring...\n")
            time.sleep(args.interval)


if __name__ == '__main__':
    main()
