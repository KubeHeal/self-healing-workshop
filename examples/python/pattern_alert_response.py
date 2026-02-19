#!/usr/bin/env python3
"""
Pattern 1: Automated Alert Response

This script demonstrates how to automatically respond to Prometheus alerts
using OpenShift Lightspeed for analysis and remediation suggestions.

Workshop: OpenShift Self-Healing with Lightspeed - Module 2, Part 9
Source: https://github.com/KubeHeal/self-healing-workshop

Usage:
    python pattern_alert_response.py
    python pattern_alert_response.py --server http://ols-server:8000
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


def extract_insights(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract actionable insights from Lightspeed response.

    Args:
        response: Lightspeed response dictionary

    Returns:
        Extracted insights with confidence scores
    """
    if 'error' in response:
        return {'status': 'error', 'message': response['error']}

    # Extract key information
    insights = {
        'status': 'success',
        'timestamp': datetime.now().isoformat(),
        'answer': response.get('answer', ''),
        'confidence': response.get('confidence', 0.0),
        'sources': response.get('sources', []),
        'recommendations': response.get('recommendations', [])
    }

    return insights


def handle_prometheus_alert(alert: Dict[str, Any], server_url: str) -> Dict[str, Any]:
    """
    Respond to Prometheus alert with Lightspeed analysis.

    Args:
        alert: Prometheus alert dictionary with labels and annotations
        server_url: Lightspeed server URL

    Returns:
        Dictionary with action ('auto_remediate' or 'escalate') and details
    """

    # Build context from alert
    context = {
        'alert_name': alert['labels']['alertname'],
        'namespace': alert['labels'].get('namespace', 'default'),
        'severity': alert['labels'].get('severity', 'warning'),
        'description': alert['annotations'].get('description', ''),
    }

    # Query Lightspeed for analysis
    client = LightspeedClient(server_url)

    analysis = client.query(
        f"Analyze this alert and suggest remediation: {context['description']}",
        context=context
    )

    # Extract recommendations
    insights = extract_insights(analysis)

    if insights['status'] == 'error':
        return {
            'action': 'error',
            'message': insights['message']
        }

    # Decide on action based on confidence
    if insights['confidence'] > 0.8:
        # High confidence - auto-remediate
        return {
            'action': 'auto_remediate',
            'alert': alert['labels']['alertname'],
            'confidence': insights['confidence'],
            'recommendations': insights['recommendations'],
            'analysis': insights['answer']
        }
    else:
        # Low confidence - escalate to human
        return {
            'action': 'escalate',
            'alert': alert['labels']['alertname'],
            'confidence': insights['confidence'],
            'analysis': insights,
            'reason': 'Low confidence in automated remediation'
        }


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Automated Prometheus Alert Response with Lightspeed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default server URL from environment
  python pattern_alert_response.py

  # Specify server URL
  python pattern_alert_response.py --server http://ols-server:8000

Environment Variables:
  OLS_SERVER_URL    Lightspeed server URL (default: http://ols-server:8000)
        """
    )

    parser.add_argument(
        '--server',
        default=os.getenv('OLS_SERVER_URL', 'http://ols-server:8000'),
        help='Lightspeed server URL'
    )

    args = parser.parse_args()

    # Sample Prometheus alert for demonstration
    sample_alert = {
        'labels': {
            'alertname': 'HighPodCPU',
            'namespace': 'self-healing-platform',
            'pod': 'coordination-engine-0',
            'severity': 'warning'
        },
        'annotations': {
            'description': 'Pod coordination-engine-0 in namespace self-healing-platform is using 85% CPU',
            'summary': 'High CPU usage detected'
        }
    }

    print("="*60)
    print("Automated Alert Response Pattern")
    print("="*60)
    print(f"\nLightspeed Server: {args.server}")
    print(f"\nSample Alert:")
    print(json.dumps(sample_alert, indent=2))

    print("\nProcessing alert with Lightspeed...")
    result = handle_prometheus_alert(sample_alert, args.server)

    print("\n" + "="*60)
    print("Result:")
    print("="*60)
    print(json.dumps(result, indent=2))

    if result['action'] == 'auto_remediate':
        print("\n✅ Action: AUTO-REMEDIATE (High confidence)")
        print(f"   Confidence: {result['confidence']:.2%}")
    elif result['action'] == 'escalate':
        print("\n⚠️  Action: ESCALATE TO HUMAN (Low confidence)")
        print(f"   Confidence: {result['confidence']:.2%}")
    else:
        print("\n❌ Action: ERROR")

    print("\n" + "="*60)


if __name__ == '__main__':
    main()
