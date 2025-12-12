# Cloud Functions Deployment Guide

This guide walks you through deploying the EHMS MyClub API pipeline to Google Cloud Functions with daily scheduling.

## Prerequisites

- Google Cloud Project with billing enabled
- `gcloud` CLI installed and configured
- MyClub API token
- Basic familiarity with command line

## Cost Estimate

- **~$0.00 - $0.15/month** (likely FREE within GCP free tier)
- 3-minute execution × 30 times/month = well within free tier limits

## One-Time Setup (Required)

### 1. Set Your GCP Project

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create ehms-mc-api \
    --display-name="EHMS MyClub API Service Account" \
    --project=${PROJECT_ID}

# Grant BigQuery permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"

# Grant Cloud Functions permissions (needed for invoking)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudfunctions.invoker"
```

### 3. Store Secrets in Secret Manager

```bash
# Store your MyClub API token
echo -n "YOUR_MC_TOKEN_HERE" | gcloud secrets create mc-token \
    --data-file=- \
    --replication-policy="automatic" \
    --project=${PROJECT_ID}

# Grant service account access to the secret
gcloud secrets add-iam-policy-binding mc-token \
    --member="serviceAccount:ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=${PROJECT_ID}
```

### 4. Configure Deployment Script

Edit `deploy.sh` and update these variables:

```bash
PROJECT_ID="your-gcp-project-id"          # Your GCP project ID
REGION="us-central1"                       # Choose your region
BIGQUERY_DATASET="ehms_myclub"            # Your BigQuery dataset name
SCHEDULE="0 2 * * *"                      # Daily at 2 AM (or customize)
```

**Schedule Examples**:
- `"0 2 * * *"` - Daily at 2 AM
- `"0 */12 * * *"` - Every 12 hours
- `"0 0 * * 1"` - Every Monday at midnight
- `"0 3 * * 1-5"` - Weekdays at 3 AM
- `"30 1 * * *"` - Daily at 1:30 AM

### 5. Create BigQuery Dataset (if not exists)

```bash
bq mk --dataset \
    --location=US \
    --project_id=${PROJECT_ID} \
    ${PROJECT_ID}:ehms_myclub
```

## Deployment

### Option 1: Using the Deploy Script (Recommended)

```bash
# Make the script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Option 2: Manual Deployment

```bash
gcloud functions deploy ehms-mc-api \
    --gen2 \
    --runtime=python313 \
    --region=us-central1 \
    --source=. \
    --entry-point=run_pipeline \
    --trigger-http \
    --no-allow-unauthenticated \
    --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},BIGQUERY_DATASET_ID=ehms_myclub" \
    --set-secrets "MC_TOKEN=mc-token:latest" \
    --service-account=ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com \
    --timeout=540s \
    --memory=512MB \
    --max-instances=1 \
    --project=${PROJECT_ID}

# Get function URL
FUNCTION_URL=$(gcloud functions describe ehms-mc-api \
    --region=us-central1 \
    --gen2 \
    --format="value(serviceConfig.uri)" \
    --project=${PROJECT_ID})

# Create scheduler
gcloud scheduler jobs create http ehms-mc-api-daily \
    --location=us-central1 \
    --schedule="0 2 * * *" \
    --uri="${FUNCTION_URL}" \
    --http-method=POST \
    --oidc-service-account-email=ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com \
    --project=${PROJECT_ID}
```

## Testing

### 1. Test the Function Directly

```bash
# Invoke the function manually
gcloud functions call ehms-mc-api \
    --region=us-central1 \
    --gen2 \
    --project=${PROJECT_ID}
```

### 2. Test with Custom Interval

```bash
# Get function URL
FUNCTION_URL=$(gcloud functions describe ehms-mc-api \
    --region=us-central1 \
    --gen2 \
    --format="value(serviceConfig.uri)" \
    --project=${PROJECT_ID})

# Test with 30-day interval
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
    "${FUNCTION_URL}?interval=30"
```

### 3. Trigger Scheduler Manually

```bash
gcloud scheduler jobs run ehms-mc-api-daily \
    --location=us-central1 \
    --project=${PROJECT_ID}
```

## Monitoring & Logs

### View Function Logs

```bash
# Recent logs
gcloud functions logs read ehms-mc-api \
    --region=us-central1 \
    --gen2 \
    --limit=50 \
    --project=${PROJECT_ID}

# Live tail
gcloud functions logs read ehms-mc-api \
    --region=us-central1 \
    --gen2 \
    --limit=50 \
    --project=${PROJECT_ID} \
    --follow
```

### View in Cloud Console

**Functions**: https://console.cloud.google.com/functions/list?project=${PROJECT_ID}

**Scheduler**: https://console.cloud.google.com/cloudscheduler?project=${PROJECT_ID}

**Logs**: https://console.cloud.google.com/logs?project=${PROJECT_ID}

### Set Up Budget Alerts

```bash
# Set a $5/month budget alert (optional but recommended)
gcloud billing budgets create \
    --billing-account=YOUR_BILLING_ACCOUNT_ID \
    --display-name="EHMS MyClub API Budget" \
    --budget-amount=5 \
    --threshold-rule=percent=50 \
    --threshold-rule=percent=90 \
    --threshold-rule=percent=100
```

## Updating the Function

After making code changes:

```bash
# Simply run the deploy script again
./deploy.sh
```

Or deploy manually:

```bash
gcloud functions deploy ehms-mc-api \
    --gen2 \
    --region=us-central1 \
    --source=. \
    --project=${PROJECT_ID}
```

## Troubleshooting

### Function Timeout

If execution takes longer than 9 minutes, increase timeout:

```bash
# Edit deploy.sh and change:
--timeout=540s  # to --timeout=900s (15 min max)
```

### Memory Issues

If function runs out of memory:

```bash
# Edit deploy.sh and change:
--memory=512MB  # to --memory=1GB or --memory=2GB
```

### Authentication Errors

```bash
# Verify service account has correct permissions
gcloud projects get-iam-policy ${PROJECT_ID} \
    --flatten="bindings[].members" \
    --filter="bindings.members:ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com"
```

### Secret Access Issues

```bash
# Verify secret exists and is accessible
gcloud secrets describe mc-token --project=${PROJECT_ID}

# Re-grant access
gcloud secrets add-iam-policy-binding mc-token \
    --member="serviceAccount:ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=${PROJECT_ID}
```

### Scheduler Not Triggering

```bash
# Check scheduler job status
gcloud scheduler jobs describe ehms-mc-api-daily \
    --location=us-central1 \
    --project=${PROJECT_ID}

# Pause and resume
gcloud scheduler jobs pause ehms-mc-api-daily --location=us-central1
gcloud scheduler jobs resume ehms-mc-api-daily --location=us-central1
```

## Cost Monitoring

### View Current Costs

```bash
# View billing for the project
gcloud billing accounts list
gcloud billing projects describe ${PROJECT_ID}
```

Or visit: https://console.cloud.google.com/billing/

### Expected Costs

With 3-minute execution once daily:
- **Cloud Functions**: ~$0.14/month (or FREE in free tier)
- **Cloud Scheduler**: FREE (first 3 jobs)
- **Secret Manager**: FREE (first 6 secrets)
- **BigQuery**: FREE (within 10GB storage + 1TB query limits)

**Total: ~$0.00 - $0.15/month**

## Clean Up (Delete Everything)

If you want to remove all resources:

```bash
# Delete function
gcloud functions delete ehms-mc-api \
    --region=us-central1 \
    --gen2 \
    --project=${PROJECT_ID}

# Delete scheduler job
gcloud scheduler jobs delete ehms-mc-api-daily \
    --location=us-central1 \
    --project=${PROJECT_ID}

# Delete secret
gcloud secrets delete mc-token --project=${PROJECT_ID}

# Delete service account
gcloud iam service-accounts delete \
    ehms-mc-api@${PROJECT_ID}.iam.gserviceaccount.com \
    --project=${PROJECT_ID}

# Delete BigQuery dataset (WARNING: deletes all data!)
bq rm -r -f -d ${PROJECT_ID}:ehms_myclub
```

## Support

For issues:
1. Check function logs first
2. Verify all environment variables are set correctly
3. Ensure service account has proper permissions
4. Check GCP quotas and billing status

## Next Steps

After deployment:
1. Monitor the first few runs in Cloud Console
2. Set up budget alerts
3. Verify data is being uploaded to BigQuery
4. Adjust schedule if needed
