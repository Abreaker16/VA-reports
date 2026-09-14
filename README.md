# Multi-Cloud Vulnerability Assessment Platform

A comprehensive vulnerability assessment platform that supports **GCP**, **AWS**, and **Azure** security services, designed for deployment on Google Cloud Run with automated CI/CD via Cloud Build.

## Features

- 📊 **Multi-Cloud Support**: Generate vulnerability reports from:
  - **GCP Security Command Center (SCC)**
  - **AWS Security Hub**
  - **Azure Security Center**
- 🔍 **Individual Cloud Reports**: Get reports for each cloud provider separately
- 📈 **Consolidated Dashboard**: View all findings across clouds in a single report
- 🎯 **Severity Filtering**: Filter findings by severity (critical, high, medium, low)
- ☁️ **Cloud-Native Deployment**: Optimized for GCP Cloud Run with Cloud Build CI/CD
- 🚀 **Automated Deployments**: GitHub-triggered builds and deployments

## Quick Start

### Deploy to Cloud Run (3 Steps)

1. **Clone and Configure:**
   ```bash
   git clone https://github.com/Abreaker16/VA-reports.git
   cd VA-reports
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Deploy:**
   ```bash
   ./deploy.sh
   ```

3. **Access:**
   Visit the URL provided after deployment to access the API documentation.

## API Endpoints

### Individual Cloud Reports

#### GCP Report
```
GET /api/report/gcp?org_id=<GCP_ORG_ID>&severity=<optional>
```

#### AWS Report
```
GET /api/report/aws?region=<AWS_REGION>&severity=<optional>
```

#### Azure Report
```
GET /api/report/azure?subscription_id=<AZURE_SUBSCRIPTION_ID>&severity=<optional>
```

### Consolidated Report (All Clouds)
```
GET /api/report/all?gcp_org_id=<GCP_ORG_ID>&aws_region=<AWS_REGION>&azure_subscription_id=<AZURE_SUB_ID>&severity=<optional>
```

### Health Check
```
GET /api/health
```

## Deployment Options

### Option 1: Automated Deployment (Recommended)

Use the included deployment script:

```bash
./deploy.sh [TAG] [REGION]
# Example: ./deploy.sh v1.0 us-central1
```

### Option 2: Manual Cloud Build Submission

```bash
gcloud builds submit --config cloudbuild.yaml \
    --substitutions=_TAG=latest,_REGION=us-central1
```

### Option 3: Set Up GitHub Trigger (CI/CD)

Automatically deploy on every push to main branch:

```bash
gcloud beta builds triggers create github \
    --name="va-reports-trigger" \
    --repo-name="Abreaker16/VA-reports" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --included-files="backend/**,cloudbuild.yaml"
```

### Option 4: Local Development with Docker

```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API endpoints for all clouds
│   │   ├── collectors/
│   │   │   ├── scc.py             # GCP Security Command Center collector
│   │   │   ├── aws.py             # AWS Security Hub collector
│   │   │   └── azure.py           # Azure Security Center collector
│   │   ├── services/
│   │   │   └── report.py          # Report generation service
│   │   └── main.py                # FastAPI application entry point
│   ├── requirements.txt           # Python dependencies
│   └── Dockerfile                 # Cloud Run optimized Dockerfile
├── frontend/
│   ├── index.html                 # Simple dashboard UI
│   └── Dockerfile
├── cloudbuild.yaml                # Cloud Build configuration
├── deploy.sh                      # Deployment script
├── DEPLOYMENT.md                  # Detailed deployment guide
├── docker-compose.yml             # Local development setup
└── README.md                      # This file
```

## Environment Variables

Configure these in Cloud Run after deployment:

| Variable | Description | Required For |
|----------|-------------|--------------|
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID | GCP Reports |
| `AWS_ACCESS_KEY_ID` | AWS access key | AWS Reports |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | AWS Reports |
| `AWS_DEFAULT_REGION` | AWS region | AWS Reports |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | Azure Reports |
| `AZURE_CLIENT_ID` | Azure client ID | Azure Reports (Service Principal) |
| `AZURE_CLIENT_SECRET` | Azure client secret | Azure Reports (Service Principal) |
| `AZURE_TENANT_ID` | Azure tenant ID | Azure Reports (Service Principal) |

Set environment variables:
```bash
gcloud run services update va-reports-service \
    --region us-central1 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID
```

## Authentication Setup

### GCP
The Cloud Run service account needs:
- **Security Command Center Viewer** role (`roles/securitycenter.findingsViewer`)

### AWS
Create an IAM user/role with:
- **Security Hub Read Access**
- Configure credentials via Cloud Run environment variables or Secret Manager

### Azure
Option 1: Use Managed Identity (if running on GCP with workload identity)
Option 2: Create a Service Principal with:
- **Security Center Reader** role

## Monitoring and Logs

### View Recent Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=va-reports-service" \
    --limit=50
```

### Check Service Status
```bash
gcloud run services describe va-reports-service --region us-central1
```

### View All Revisions
```bash
gcloud run revisions list --service va-reports-service --region us-central1
```

## Cost Optimization

Default Cloud Run configuration:
- **Min instances**: 0 (scales to zero when idle)
- **Max instances**: 10
- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **Concurrency**: 80 requests per instance

Adjust based on your needs:
```bash
gcloud run services update va-reports-service \
    --region us-central1 \
    --memory=1Gi \
    --min-instances=1
```

## Security Best Practices

1. **Use Secret Manager** for sensitive credentials instead of environment variables
2. **Restrict Access** by removing `--allow-unauthenticated` flag
3. **Enable VPC Connector** if accessing private resources
4. **Regular Updates** - Keep dependencies updated

## Troubleshooting

### Build Fails
```bash
# Check recent builds
gcloud builds list --limit=5

# View build logs
gcloud builds log BUILD_ID
```

### Service Won't Start
- Check Cloud Run logs (see Monitoring section)
- Verify PORT is set to 8080
- Ensure all dependencies are in requirements.txt

### Permission Errors
```bash
# Grant SCC Viewer role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
    --role="roles/securitycenter.findingsViewer"
```

## License

MIT
