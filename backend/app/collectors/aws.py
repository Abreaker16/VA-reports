"""AWS Security Hub findings collector module."""

import logging
from typing import List, Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def fetch_security_hub_findings(region: str = "us-east-1", severity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch security findings from AWS Security Hub.
    
    Args:
        region: AWS region to fetch findings from
        severity_filter: Optional severity level to filter findings
        
    Returns:
        List of finding dictionaries with resource_id, severity, and title
        
    Raises:
        ClientError: If there's an error communicating with Security Hub API
    """
    try:
        client = boto3.client('securityhub', region_name=region)
        findings: List[Dict[str, Any]] = []
        
        # Build filter based on severity
        filters = {}
        if severity_filter:
            severity_map = {
                'critical': [{'Value': 'CRITICAL', 'Comparison': 'EQUALS'}],
                'high': [{'Value': 'HIGH', 'Comparison': 'EQUALS'}],
                'medium': [{'Value': 'MEDIUM', 'Comparison': 'EQUALS'}],
                'low': [{'Value': 'LOW', 'Comparison': 'EQUALS'}]
            }
            filters['SeverityLabel'] = severity_map.get(severity_filter.lower(), [])
        
        # Paginate through findings
        paginator = client.get_paginator('get_findings')
        pages = paginator.paginate(Filters=filters)
        
        for page in pages:
            for finding in page.get('Findings', []):
                findings.append({
                    "resource_id": finding.get('Resources', [{}])[0].get('Id', 'N/A'),
                    "severity": finding.get('Severity', {}).get('Label', 'UNKNOWN').lower(),
                    "title": finding.get('Title', 'No title'),
                    "source_name": finding.get('ProductName', 'Security Hub'),
                    "finding_id": finding.get('Id', 'N/A')
                })
        
        logger.info(f"Fetched {len(findings)} findings from AWS Security Hub")
        return findings
        
    except ClientError as e:
        logger.error(f"AWS API error fetching Security Hub findings: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching Security Hub findings: {str(e)}")
        raise
