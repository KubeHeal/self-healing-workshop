#!/usr/bin/env python3
"""
Pattern 2: Batch Pod Fleet Analysis

This script demonstrates how to analyze all pods in a namespace using
OpenShift Lightspeed to identify and diagnose problematic pods.

Workshop: OpenShift Self-Healing with Lightspeed - Module 2, Part 9
Source: https://github.com/KubeHeal/self-healing-workshop

Usage:
    python pattern_batch_analysis.py
    python pattern_batch_analysis.py --namespace my-namespace
    python pattern_batch_analysis.py --server http://ols-server:8000 --namespace default
"""

import os
import sys
import argparse

try:
    import pandas as pd
except ImportError:
    print("Error: pandas not installed")
    print("Install with: pip install pandas")
    sys.exit(1)

try:
    from lightspeed_client import LightspeedClient
except ImportError:
    print("Error: lightspeed_client.py not found in the same directory")
    print("Download it from: https://raw.githubusercontent.com/KubeHeal/self-healing-workshop/main/examples/python/lightspeed_client.py")
    sys.exit(1)


def analyze_pod_fleet(namespace: str, server_url: str) -> pd.DataFrame:
    """
    Analyze all pods in namespace with Lightspeed.

    Args:
        namespace: Namespace to analyze
        server_url: Lightspeed server URL

    Returns:
        DataFrame with pod analysis results
    """

    client = LightspeedClient(server_url)

    # Get pod list
    print(f"Querying Lightspeed for pods in {namespace}...")
    pods_response = client.query(
        f"List all pods in {namespace} with their status",
        context={'namespace': namespace}
    )

    if 'error' in pods_response:
        print(f"Error getting pod list: {pods_response['error']}")
        return pd.DataFrame()

    # Extract pod information from response
    # Note: This is a simplified example. In production, you'd parse the response
    # more robustly or use the MCP tools directly for structured data.

    # For demonstration, we'll create sample data
    # In a real scenario, you'd extract this from pods_response
    sample_pods = [
        {'name': 'coordination-engine-0', 'status': 'Running'},
        {'name': 'mcp-server-abc123', 'status': 'Running'},
        {'name': 'predictive-analytics-predictor-xyz', 'status': 'CrashLoopBackOff'},
        {'name': 'anomaly-detector-predictor-abc', 'status': 'Error'},
    ]

    # Analyze each problematic pod
    results = []
    for pod in sample_pods:
        if pod['status'] != 'Running':
            print(f"  Analyzing problematic pod: {pod['name']} (status: {pod['status']})")
            analysis = client.query(
                f"Why is pod {pod['name']} not running?",
                context={'namespace': namespace, 'pod': pod['name']}
            )

            results.append({
                'pod': pod['name'],
                'status': pod['status'],
                'analysis': analysis.get('answer', 'No analysis available')[:100] + '...',
                'confidence': analysis.get('confidence', 0.0)
            })
        else:
            # Include healthy pods for completeness
            results.append({
                'pod': pod['name'],
                'status': pod['status'],
                'analysis': 'Pod is healthy',
                'confidence': 1.0
            })

    return pd.DataFrame(results)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Batch Pod Fleet Analysis with Lightspeed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze default namespace
  python pattern_batch_analysis.py

  # Analyze specific namespace
  python pattern_batch_analysis.py --namespace self-healing-platform

  # Specify server URL
  python pattern_batch_analysis.py --server http://ols-server:8000 --namespace default

Environment Variables:
  OLS_SERVER_URL    Lightspeed server URL (default: http://ols-server:8000)
  NAMESPACE         Namespace to analyze (default: self-healing-platform)
        """
    )

    parser.add_argument(
        '--server',
        default=os.getenv('OLS_SERVER_URL', 'http://ols-server:8000'),
        help='Lightspeed server URL'
    )

    parser.add_argument(
        '--namespace',
        default=os.getenv('NAMESPACE', 'self-healing-platform'),
        help='Namespace to analyze'
    )

    args = parser.parse_args()

    print("="*60)
    print("Batch Pod Fleet Analysis Pattern")
    print("="*60)
    print(f"\nLightspeed Server: {args.server}")
    print(f"Namespace: {args.namespace}\n")

    # Analyze the pod fleet
    results_df = analyze_pod_fleet(args.namespace, args.server)

    if results_df.empty:
        print("No results to display (check for errors above)")
        sys.exit(1)

    # Display results
    print("\n" + "="*60)
    print("Analysis Results:")
    print("="*60)

    # Configure pandas display options for better output
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)

    print(results_df.to_string(index=False))

    # Summary statistics
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    print(f"Total pods analyzed: {len(results_df)}")
    print(f"Healthy pods: {len(results_df[results_df['status'] == 'Running'])}")
    print(f"Problematic pods: {len(results_df[results_df['status'] != 'Running'])}")
    print(f"Average confidence: {results_df['confidence'].mean():.2%}")
    print("="*60)


if __name__ == '__main__':
    main()
