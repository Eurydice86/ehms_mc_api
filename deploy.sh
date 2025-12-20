#!/bin/bash

# EHMS MyClub API - Cloud Functions Deployment Script
# This script deploys the function and sets up the Cloud Scheduler

set -e  # Exit on error

# Configuration - UPDATE THESE VALUES
PROJECT_ID="your-gcp-project-id"
REGION="us-central1"
FUNCTION_NAME="ehms-mc-api"
SERVICE_ACCOUNT="ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com"
MC_TOKEN_SECRET="mc-token"  # Name of secret in Secret Manager
BIGQUERY_DATASET="ehms_myclub"
SCHEDULE="0 2 * * *"  # Daily at 2 AM (change as needed)

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}EHMS MyClub API - Cloud Functions Deploy${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Validate configuration
if [ "$PROJECT_ID" = "your-gcp-project-id" ]; then
    echo -e "${YELLOW}ERROR: Please update PROJECT_ID in deploy.sh${NC}"
    exit 1
fi

echo -e "${GREEN}Step 1: Deploying Cloud Function...${NC}"
gcloud functions deploy ${FUNCTION_NAME} \
    --gen2 \
    --runtime=python313 \
    --region=${REGION} \
    --source=. \
    --entry-point=run_pipeline \
    --trigger-http \
    --no-allow-unauthenticated \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},BIGQUERY_DATASET_ID=${BIGQUERY_DATASET}" \
    --set-secrets "MC_TOKEN=${MC_TOKEN_SECRET}:latest" \
    --service-account=${SERVICE_ACCOUNT} \
    --timeout=540s \
    --memory=512MB \
    --max-instances=1 \
    --project=${PROJECT_ID}

echo ""
echo -e "${GREEN}Step 2: Getting function URL...${NC}"
FUNCTION_URL=$(gcloud functions describe ${FUNCTION_NAME} \
    --region=${REGION} \
    --gen2 \
    --format="value(serviceConfig.uri)" \
    --project=${PROJECT_ID})

echo "Function URL: ${FUNCTION_URL}"
echo ""

echo -e "${GREEN}Step 3: Creating/Updating Cloud Scheduler job...${NC}"
# Check if scheduler job exists
if gcloud scheduler jobs describe ${FUNCTION_NAME}-daily --location=${REGION} --project=${PROJECT_ID} &>/dev/null; then
    echo "Scheduler job exists, updating..."
    gcloud scheduler jobs update http ${FUNCTION_NAME}-daily \
        --location=${REGION} \
        --schedule="${SCHEDULE}" \
        --uri="${FUNCTION_URL}" \
        --http-method=POST \
        --oidc-service-account-email=${SERVICE_ACCOUNT} \
        --project=${PROJECT_ID}
else
    echo "Creating new scheduler job..."
    gcloud scheduler jobs create http ${FUNCTION_NAME}-daily \
        --location=${REGION} \
        --schedule="${SCHEDULE}" \
        --uri="${FUNCTION_URL}" \
        --http-method=POST \
        --oidc-service-account-email=${SERVICE_ACCOUNT} \
        --project=${PROJECT_ID}
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Function deployed: ${FUNCTION_URL}"
echo "Schedule: ${SCHEDULE}"
echo ""
echo -e "${BLUE}Test the function manually:${NC}"
echo "gcloud functions call ${FUNCTION_NAME} --region=${REGION} --gen2"
echo ""
echo -e "${BLUE}View logs:${NC}"
echo "gcloud functions logs read ${FUNCTION_NAME} --region=${REGION} --gen2 --limit=50"
echo ""
echo -e "${BLUE}View scheduler jobs:${NC}"
echo "gcloud scheduler jobs list --location=${REGION}"
echo ""
