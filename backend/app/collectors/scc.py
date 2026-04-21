from google.cloud import securitycenter_v1

def fetch_scc_findings(org_id):
    client = securitycenter_v1.SecurityCenterClient()
    org_name = f"organizations/{org_id}"
    findings = []

    for source in client.list_sources(request={"parent": org_name}):
        res = client.list_findings(request={"parent": source.name})
        for f in res:
            finding = f.finding
            findings.append({
                "resource_id": finding.resource_name,
                "severity": finding.severity.lower(),
                "title": finding.category
            })
    return findings
