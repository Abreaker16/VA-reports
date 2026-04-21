from fastapi import APIRouter
from app.collectors.scc import fetch_scc_findings
from app.services.report import generate_summary

router = APIRouter()

@router.get("/report")
def report():
    findings = fetch_scc_findings("ORG_ID")
    return {
        "summary": generate_summary(findings),
        "findings": findings
    }
