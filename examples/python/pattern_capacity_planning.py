#!/usr/bin/env python3
"""
Pattern 3: Capacity Planning Report

This script demonstrates how to generate capacity planning reports using
OpenShift Lightspeed to predict resource usage and get recommendations.

Workshop: OpenShift Self-Healing with Lightspeed - Module 2, Part 9
Source: https://github.com/KubeHeal/self-healing-workshop

Usage:
    python pattern_capacity_planning.py
    python pattern_capacity_planning.py --namespace my-namespace
    python pattern_capacity_planning.py --server http://ols-server:8000 --output report.json
"""

import os
import sys
import argparse
import json
from datetime import datetime
from typing import Dict, Any

try:
    from lightspeed_client import LightspeedClient
except ImportError:
    print("Error: lightspeed_client.py not found in the same directory")
    print("Download it from: https://raw.githubusercontent.com/KubeHeal/self-healing-workshop/main/examples/python/lightspeed_client.py")
    sys.exit(1)


def generate_capacity_report(namespace: str, server_url: str) -> Dict[str, Any]:
    """
    Generate capacity planning report with predictions.

    Args:
        namespace: Namespace to analyze
        server_url: Lightspeed server URL

    Returns:
        Dictionary with current usage, predictions, and recommendations
    """

    client = LightspeedClient(server_url)

    print(f"Generating capacity report for {namespace}...")

    # Get current usage
    print("  1/3 Fetching current resource usage...")
    current = client.query(
        f"What's the current resource usage in {namespace}?",
        context={'namespace': namespace}
    )

    # Get predictions for key times
    print("  2/3 Generating time-based predictions...")
    predictions = {}
    for time in ['9 AM', '12 PM', '3 PM', '6 PM']:
        pred = client.query(
            f"What will resource usage be at {time}?",
            context={'namespace': namespace}
        )
        predictions[time] = {
            'answer': pred.get('answer', 'No prediction available'),
            'confidence': pred.get('confidence', 0.0)
        }

    # Get capacity recommendations
    print("  3/3 Fetching capacity recommendations...")
    recommendations = client.get_recommendations(
        'capacity_planning',
        {'namespace': namespace, 'timeframe': '7 days'}
    )

    # Build report
    report = {
        'namespace': namespace,
        'generated_at': datetime.now().isoformat(),
        'current_usage': {
            'answer': current.get('answer', 'No data available'),
            'confidence': current.get('confidence', 0.0)
        },
        'predictions': predictions,
        'recommendations': recommendations if 'error' not in recommendations else {'error': recommendations['error']},
        'metadata': {
            'server': server_url,
            'report_version': '1.0'
        }
    }

    return report


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Capacity Planning Report Generator with Lightspeed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report for default namespace (print to console)
  python pattern_capacity_planning.py

  # Generate report for specific namespace
  python pattern_capacity_planning.py --namespace self-healing-platform

  # Save report to JSON file
  python pattern_capacity_planning.py --output capacity-report.json

  # Specify server URL
  python pattern_capacity_planning.py --server http://ols-server:8000

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

    parser.add_argument(
        '--output',
        help='Output JSON file path (default: print to console)'
    )

    args = parser.parse_args()

    print("="*60)
    print("Capacity Planning Report Generator")
    print("="*60)
    print(f"\nLightspeed Server: {args.server}")
    print(f"Namespace: {args.namespace}\n")

    # Generate the report
    report = generate_capacity_report(args.namespace, args.server)

    # Format as JSON
    report_json = json.dumps(report, indent=2)

    # Output results
    if args.output:
        # Save to file
        with open(args.output, 'w') as f:
            f.write(report_json)
        print(f"✅ Report saved to: {args.output}")

        # Also print summary to console
        print("\n" + "="*60)
        print("Report Summary:")
        print("="*60)
        print(f"Generated: {report['generated_at']}")
        print(f"Namespace: {report['namespace']}")
        print(f"\nCurrent Usage Confidence: {report['current_usage']['confidence']:.2%}")
        print(f"Predictions Generated: {len(report['predictions'])}")
        print("="*60)
    else:
        # Print full report to console
        print("\n" + "="*60)
        print("Capacity Planning Report:")
        print("="*60)
        print(report_json)
        print("\n" + "="*60)


if __name__ == '__main__':
    main()
