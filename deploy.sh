#!/bin/bash
set -e

# Deployment script for Multi-Cloud VA Reports to Cloud Run
# Usage: ./deploy.sh [TAG] [REGION]

PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
REGION=${2:-${REGION:-us-central1}}
TAG=${1:-${TAG:-latest}}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID is not set and no default found in gcloud config"
    echo "Please set it with: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "=========================================="
echo "Multi-Cloud VA Reports Deployment"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Region:     $REGION"
echo "Tag:        $TAG"
echo "=========================================="

# Verify required APIs are enabled
echo "Checking required APIs..."
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    securitycenter.googleapis.com \
    --quiet || true

# Submit build to Cloud Build
echo ""
echo "Submitting build to Cloud Build..."
gcloud builds submit \
    --config cloudbuild.yaml \
    --substitutions=_TAG=$TAG,_REGION=$REGION \
    --project=$PROJECT_ID \
    --timeout=1200

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Service URL:"
gcloud run services describe va-reports-service \
    --region $REGION \
    --format 'value(status.url)'
echo ""
echo "API Documentation:"
echo "$(gcloud run services describe va-reports-service --region $REGION --format 'value(status.url)')/docs"
echo ""
echo "To view logs:"
echo "gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=va-reports-service\" --limit=50"
echo ""
