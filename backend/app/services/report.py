"""Report generation service for security findings."""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def generate_summary(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Generate a summary of security findings by severity.
    
    Args:
        findings: List of finding dictionaries containing severity information
        
    Returns:
        Dictionary with counts for total, critical, high, medium, and low severity findings
    """
    if not findings:
        return {
            "total": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
    
    summary = {
        "total": len(findings),
        "critical": sum(1 for f in findings if f.get("severity") == "critical"),
        "high": sum(1 for f in findings if f.get("severity") == "high"),
        "medium": sum(1 for f in findings if f.get("severity") == "medium"),
        "low": sum(1 for f in findings if f.get("severity") == "low")
    }
    
    logger.debug(f"Generated summary: {summary}")
    return summary


def generate_detailed_report(findings: List[Dict[str, Any]], org_id: str) -> Dict[str, Any]:
    """
    Generate a detailed report with findings grouped by severity.
    
    Args:
        findings: List of finding dictionaries
        org_id: Organization ID for the report
        
    Returns:
        Dictionary containing summary, grouped findings, and metadata
    """
    grouped_findings = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": []
    }
    
    for finding in findings:
        severity = finding.get("severity", "low")
        if severity in grouped_findings:
            grouped_findings[severity].append(finding)
    
    return {
        "organization_id": org_id,
        "summary": generate_summary(findings),
        "findings_by_severity": grouped_findings,
        "all_findings": findings
    }
