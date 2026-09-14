# Deployment Guide for Cloud Run with Cloud Build

This guide explains how to deploy the Multi-Cloud VA Reports application to Google Cloud Run using Cloud Build triggers.

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **gcloud CLI** installed and configured
3. **Required APIs** enabled:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
   - Security Command Center API (for GCP reports)

## Setup Instructions

### 1. Enable Required APIs

```bash
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    securitycenter.googleapis.com
```

### 2. Configure gcloud

```bash
# Set your project ID
export PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# Set region for Cloud Run
export REGION="us-central1"
```

### 3. Grant Required Permissions

```bash
# Get your Cloud Build service account
CLOUD_BUILD_SA=$(gcloud projects get-iam-policy $PROJECT_ID \
    --filter="bindings.members:cloudbuild" \
    --format="value(bindings.members)" \
    | grep "serviceAccount" \
    | head -1)

# Grant Cloud Build permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/storage.admin"

# Grant SCC Viewer role for vulnerability reports
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/securitycenter.findingsViewer"
```

### 4. Deploy Using Cloud Build (One-time Manual Trigger)

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml \
    --substitutions=_TAG=latest,_REGION=$REGION \
    --project=$PROJECT_ID
```

### 5. Set Up Cloud Build Trigger (Automated CI/CD)

#### Option A: GitHub Trigger

```bash
# Create a Cloud Build trigger for GitHub repository
gcloud beta builds triggers create github \
    --name="va-reports-trigger" \
    --repo-name="Abreaker16/VA-reports" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild.yaml" \
    --control-files="cloudbuild.yaml" \
    --included-files="backend/**,cloudbuild.yaml" \
    --substitutions="_TAG=latest,_REGION=$REGION"
```

#### Option B: Manual Trigger Script

Create a script `deploy.sh`:

```bash
#!/bin/bash
set -e

PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}
TAG=${TAG:-latest}

echo "Deploying to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Tag: $TAG"

gcloud builds submit \
    --config cloudbuild.yaml \
    --substitutions=_TAG=$TAG,_REGION=$REGION \
    --project=$PROJECT_ID

echo "Deployment complete!"
echo "Service URL: https://va-reports-service-$REGION.run.app"
```

Make it executable:
```bash
chmod +x deploy.sh
```

## Environment Variables

Configure these environment variables in Cloud Run after deployment:

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID | `my-project-123` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to GCP service account (if needed) | `/secrets/sa-key.json` |
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `...` |
| `AWS_DEFAULT_REGION` | AWS region | `us-east-1` |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID | `xxx-xxx-xxx` |
| `AZURE_CLIENT_ID` | Azure client ID (if using service principal) | `...` |
| `AZURE_CLIENT_SECRET` | Azure client secret | `...` |
| `AZURE_TENANT_ID` | Azure tenant ID | `...` |

Set environment variables:
```bash
gcloud run services update va-reports-service \
    --region $REGION \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID
```

## Accessing the Application

After deployment, get the service URL:

```bash
gcloud run services describe va-reports-service \
    --region $REGION \
    --format 'value(status.url)'
```

### API Endpoints

- **Health Check**: `https://va-reports-service-REGION.run.app/api/health`
- **GCP Report**: `https://va-reports-service-REGION.run.app/api/report/gcp?org_id=YOUR_ORG_ID`
- **AWS Report**: `https://va-reports-service-REGION.run.app/api/report/aws?region=us-east-1`
- **Azure Report**: `https://va-reports-service-REGION.run.app/api/report/azure?subscription_id=YOUR_SUB_ID`
- **All Clouds**: `https://va-reports-service-REGION.run.app/api/report/all?aws_region=us-east-1`
- **API Docs**: `https://va-reports-service-REGION.run.app/docs`

## Monitoring and Logs

### View Logs
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=va-reports-service" \
    --limit=50 \
    --format="table(timestamp,textPayload)"
```

### Check Service Status
```bash
gcloud run services describe va-reports-service --region $REGION
```

### View Revisions
```bash
gcloud run revisions list --service va-reports-service --region $REGION
```

## Troubleshooting

### Build Fails
- Check Cloud Build logs: `gcloud builds list --limit=5`
- View detailed build log: `gcloud builds log BUILD_ID`

### Service Won't Start
- Check Cloud Run logs (see above)
- Verify PORT environment variable is set to 8080
- Ensure all dependencies are in requirements.txt

### Permission Errors
- Verify service account has required roles
- Check IAM bindings for Cloud Build service account

## Cost Optimization

The default configuration includes:
- **Min instances**: 0 (scales to zero when idle)
- **Max instances**: 10 (limits concurrent requests)
- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **Concurrency**: 80 requests per instance

Adjust based on your needs:
```bash
gcloud run services update va-reports-service \
    --region $REGION \
    --memory=1Gi \
    --cpu=2 \
    --min-instances=1 \
    --max-instances=20
```

## Security Best Practices

1. **Use Secret Manager** for sensitive credentials:
   ```bash
   gcloud secrets create aws-credentials --data-file=aws-creds.json
   gcloud run services update va-reports-service \
       --region $REGION \
       --update-secrets=AWS_CREDS=aws-credentials:latest
   ```

2. **Restrict Access** (remove `--allow-unauthenticated`):
   ```bash
   gcloud run services update va-reports-service \
       --region $REGION \
       --no-allow-unauthenticated
   ```

3. **Enable VPC Connector** if accessing private resources

## Updating the Application

Every time you push changes to the repository:
- Cloud Build trigger will automatically build and deploy
- New revision will be created in Cloud Run
- Traffic will be shifted to the new revision

To manually trigger a deployment:
```bash
./deploy.sh
# or
gcloud builds submit --config cloudbuild.yaml
```
