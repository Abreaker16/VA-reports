import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Query

from app.collectors.scc import fetch_scc_findings
from app.services.report import generate_summary

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/report", response_model=Dict[str, Any])
def get_report(
    org_id: str = Query(..., description="GCP Organization ID"),
    severity: str | None = Query(None, description="Filter findings by severity")
):
    """
    Generate a security report based on SCC findings.
    
    Args:
        org_id: GCP Organization ID to fetch findings from
        severity: Optional severity filter (critical, high, medium, low)
    
    Returns:
        Dictionary containing summary and findings list
    """
    try:
        findings = fetch_scc_findings(org_id)
        
        # Apply severity filter if provided
        if severity:
            findings = [f for f in findings if f["severity"] == severity.lower()]
        
        return {
            "summary": generate_summary(findings),
            "findings": findings
        }
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
