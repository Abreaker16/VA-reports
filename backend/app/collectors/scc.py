"""Security Command Center findings collector module."""

import logging
from typing import List, Dict, Any, Optional

from google.cloud import securitycenter_v1
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)


def fetch_scc_findings(org_id: str, severity_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch security findings from GCP Security Command Center.
    
    Args:
        org_id: GCP Organization ID
        severity_filter: Optional severity level to filter findings
        
    Returns:
        List of finding dictionaries with resource_id, severity, and title
        
    Raises:
        GoogleAPIError: If there's an error communicating with SCC API
    """
    try:
        client = securitycenter_v1.SecurityCenterClient()
        org_name = f"organizations/{org_id}"
        findings: List[Dict[str, Any]] = []

        for source in client.list_sources(request={"parent": org_name}):
            res = client.list_findings(request={"parent": source.name})
            for f in res:
                finding = f.finding
                
                # Apply severity filter if specified
                if severity_filter and finding.severity.name.lower() != severity_filter.lower():
                    continue
                    
                findings.append({
                    "resource_id": finding.resource_name,
                    "severity": finding.severity.name.lower(),
                    "title": finding.category,
                    "source_name": source.display_name,
                    "finding_id": finding.name
                })
        
        logger.info(f"Fetched {len(findings)} findings for organization {org_id}")
        return findings
        
    except GoogleAPIError as e:
        logger.error(f"Google API error fetching SCC findings: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching SCC findings: {str(e)}")
        raise
