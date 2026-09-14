import logging
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Query

from app.collectors.scc import fetch_scc_findings
from app.collectors.aws import fetch_security_hub_findings
from app.collectors.azure import fetch_security_center_findings
from app.services.report import generate_summary

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/report/gcp", response_model=Dict[str, Any])
def get_gcp_report(
    org_id: str = Query(..., description="GCP Organization ID"),
    severity: str | None = Query(None, description="Filter findings by severity")
):
    """
    Generate a security report based on GCP SCC findings.
    
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
            "cloud": "GCP",
            "summary": generate_summary(findings),
            "findings": findings
        }
    except Exception as e:
        logger.error(f"Error generating GCP report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate GCP report: {str(e)}")


@router.get("/report/aws", response_model=Dict[str, Any])
def get_aws_report(
    region: str = Query("us-east-1", description="AWS Region"),
    severity: str | None = Query(None, description="Filter findings by severity")
):
    """
    Generate a security report based on AWS Security Hub findings.
    
    Args:
        region: AWS Region to fetch findings from
        severity: Optional severity filter (critical, high, medium, low)
    
    Returns:
        Dictionary containing summary and findings list
    """
    try:
        findings = fetch_security_hub_findings(region)
        
        # Apply severity filter if provided
        if severity:
            findings = [f for f in findings if f["severity"] == severity.lower()]
        
        return {
            "cloud": "AWS",
            "summary": generate_summary(findings),
            "findings": findings
        }
    except Exception as e:
        logger.error(f"Error generating AWS report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AWS report: {str(e)}")


@router.get("/report/azure", response_model=Dict[str, Any])
def get_azure_report(
    subscription_id: str = Query(..., description="Azure Subscription ID"),
    severity: str | None = Query(None, description="Filter findings by severity")
):
    """
    Generate a security report based on Azure Security Center findings.
    
    Args:
        subscription_id: Azure Subscription ID to fetch findings from
        severity: Optional severity filter (critical, high, medium, low)
    
    Returns:
        Dictionary containing summary and findings list
    """
    try:
        findings = fetch_security_center_findings(subscription_id)
        
        # Apply severity filter if provided
        if severity:
            findings = [f for f in findings if f["severity"] == severity.lower()]
        
        return {
            "cloud": "Azure",
            "summary": generate_summary(findings),
            "findings": findings
        }
    except Exception as e:
        logger.error(f"Error generating Azure report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate Azure report: {str(e)}")


@router.get("/report/all", response_model=Dict[str, Any])
def get_all_reports(
    gcp_org_id: str | None = Query(None, description="GCP Organization ID"),
    aws_region: str = Query("us-east-1", description="AWS Region"),
    azure_subscription_id: str | None = Query(None, description="Azure Subscription ID"),
    severity: str | None = Query(None, description="Filter findings by severity")
):
    """
    Generate a consolidated security report from all three clouds.
    
    Args:
        gcp_org_id: GCP Organization ID (optional)
        aws_region: AWS Region
        azure_subscription_id: Azure Subscription ID (optional)
        severity: Optional severity filter (critical, high, medium, low)
    
    Returns:
        Dictionary containing reports from all configured clouds
    """
    try:
        reports = {}
        
        # Fetch GCP report if org_id provided
        if gcp_org_id:
            try:
                gcp_findings = fetch_scc_findings(gcp_org_id)
                if severity:
                    gcp_findings = [f for f in gcp_findings if f["severity"] == severity.lower()]
                reports["GCP"] = {
                    "summary": generate_summary(gcp_findings),
                    "findings": gcp_findings
                }
            except Exception as e:
                logger.warning(f"Failed to fetch GCP report: {str(e)}")
                reports["GCP"] = {"error": str(e)}
        
        # Fetch AWS report
        try:
            aws_findings = fetch_security_hub_findings(aws_region)
            if severity:
                aws_findings = [f for f in aws_findings if f["severity"] == severity.lower()]
            reports["AWS"] = {
                "summary": generate_summary(aws_findings),
                "findings": aws_findings
            }
        except Exception as e:
            logger.warning(f"Failed to fetch AWS report: {str(e)}")
            reports["AWS"] = {"error": str(e)}
        
        # Fetch Azure report if subscription_id provided
        if azure_subscription_id:
            try:
                azure_findings = fetch_security_center_findings(azure_subscription_id)
                if severity:
                    azure_findings = [f for f in azure_findings if f["severity"] == severity.lower()]
                reports["Azure"] = {
                    "summary": generate_summary(azure_findings),
                    "findings": azure_findings
                }
            except Exception as e:
                logger.warning(f"Failed to fetch Azure report: {str(e)}")
                reports["Azure"] = {"error": str(e)}
        
        # Calculate total summary
        total_summary = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
        for cloud_report in reports.values():
            if "summary" in cloud_report:
                for key in total_summary:
                    total_summary[key] += cloud_report["summary"].get(key, 0)
        
        return {
            "clouds": list(reports.keys()),
            "total_summary": total_summary,
            "reports_by_cloud": reports
        }
    except Exception as e:
        logger.error(f"Error generating consolidated report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate consolidated report: {str(e)}")


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
