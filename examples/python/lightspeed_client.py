#!/usr/bin/env python3
"""
LightspeedClient - Python client for OpenShift Lightspeed

This script provides a reusable client library for interacting with
OpenShift Lightspeed's API for cluster management and AI-powered operations.

Workshop: OpenShift Self-Healing with Lightspeed - Module 2, Part 7
Source: https://github.com/KubeHeal/self-healing-workshop

Usage:
    python lightspeed_client.py

    # Or use as a library:
    from lightspeed_client import LightspeedClient
    client = LightspeedClient('http://ols-server:8000')
    response = client.query("What is the cluster health?")
"""

import os
import sys
import argparse
import requests
from typing import Dict, Any


class LightspeedClient:
    """Client for OpenShift Lightspeed communication."""

    def __init__(self, server_url: str, timeout: int = 30):
        """
        Initialize Lightspeed client.

        Args:
            server_url: Base URL of the Lightspeed server
            timeout: Request timeout in seconds (default: 30)
        """
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def query(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Send query to Lightspeed.

        Args:
            question: Natural language question
            context: Optional context dictionary (namespace, pod names, etc.)

        Returns:
            Dictionary with 'answer', 'confidence', 'sources', etc.
            or {'error': 'message'} on failure
        """
        try:
            payload = {
                'question': question,
                'context': context or {}
            }

            response = self.session.post(
                f"{self.server_url}/query",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.RequestException as e:
            return {'error': f"Request failed: {str(e)}"}
        except Exception as e:
            return {'error': f"Unexpected error: {str(e)}"}

    def get_recommendations(self, issue_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI recommendations for a specific issue.

        Args:
            issue_type: Type of issue (e.g., 'high_resource_usage', 'pod_crash')
            context: Issue context (pod name, namespace, metrics, etc.)

        Returns:
            Dictionary with recommendations and confidence scores
            or {'error': 'message'} on failure
        """
        try:
            payload = {
                'issue_type': issue_type,
                'context': context
            }

            response = self.session.post(
                f"{self.server_url}/recommendations",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.RequestException as e:
            return {'error': f"Request failed: {str(e)}"}
        except Exception as e:
            return {'error': f"Unexpected error: {str(e)}"}


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='OpenShift Lightspeed Python Client',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default server URL from environment
  python lightspeed_client.py

  # Specify server URL
  python lightspeed_client.py --server http://ols-server:8000

Environment Variables:
  OLS_SERVER_URL    Lightspeed server URL
                  Inside cluster: http://lightspeed-app-server.openshift-lightspeed.svc:8080
                  Via port-forward: http://localhost:8080
  NAMESPACE         Default namespace for queries (default: self-healing-platform)
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
        help='Namespace for queries'
    )

    args = parser.parse_args()

    # Initialize client
    print(f"Connecting to Lightspeed at {args.server}...")
    client = LightspeedClient(args.server)

    # Example 1: Simple query
    print("\n" + "="*60)
    print("Example 1: Simple Query")
    print("="*60)
    response = client.query(
        "How do I troubleshoot high CPU usage in OpenShift pods?",
        context={'namespace': args.namespace}
    )

    if 'error' in response:
        print(f"Error: {response['error']}")
    else:
        print(f"Answer: {response.get('answer', 'No answer provided')}")
        if 'confidence' in response:
            print(f"Confidence: {response['confidence']:.2%}")

    # Example 2: Get recommendations
    print("\n" + "="*60)
    print("Example 2: Get Recommendations")
    print("="*60)
    issue_context = {
        'pod_name': 'coordination-engine-0',
        'namespace': args.namespace,
        'cpu_usage': 85,
        'memory_usage': 72,
        'restart_count': 2
    }

    recommendations = client.get_recommendations(
        'high_resource_usage',
        issue_context
    )

    if 'error' in recommendations:
        print(f"Error: {recommendations['error']}")
    else:
        print(f"Recommendations: {recommendations}")

    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60)


if __name__ == '__main__':
    main()
