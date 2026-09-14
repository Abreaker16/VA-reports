"""Azure Security Center findings collector module."""

import logging
from typing import List, Dict, Any, Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.security import SecurityCenter
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)


def fetch_security_center_findings(subscription_id: str, severity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch security findings from Azure Security Center.
    
    Args:
        subscription_id: Azure Subscription ID to fetch findings from
        severity_filter: Optional severity level to filter findings
        
    Returns:
        List of finding dictionaries with resource_id, severity, and title
        
    Raises:
        AzureError: If there's an error communicating with Azure Security Center API
    """
    try:
        credential = DefaultAzureCredential()
        client = SecurityCenter(credential, subscription_id)
        findings: List[Dict[str, Any]] = []
        
        # Map severity filter
        severity_map = {
            'critical': 'High',  # Azure uses High for critical
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low'
        }
        
        # Get all assessments (findings)
        for assessment in client.alerts.list():
            severity = assessment.properties.severity or 'Unknown'
            
            # Apply severity filter if specified
            if severity_filter:
                expected_severity = severity_map.get(severity_filter.lower(), severity)
                if severity.lower() != expected_severity.lower():
                    continue
            
            findings.append({
                "resource_id": assessment.properties.compound_alert_id or 'N/A',
                "severity": severity.lower(),
                "title": assessment.properties.display_name or 'No title',
                "source_name": "Azure Security Center",
                "finding_id": assessment.name or 'N/A'
            })
        
        logger.info(f"Fetched {len(findings)} findings from Azure Security Center")
        return findings
        
    except AzureError as e:
        logger.error(f"Azure API error fetching Security Center findings: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching Security Center findings: {str(e)}")
        raise
