# EHMS MyClub API

An automated data extraction and synchronization system that fetches member, event, course, and attendance data from the MyClub API and uploads it directly to Google BigQuery.

## Overview

This application:
- Fetches member, event, course, and attendance data from the MyClub API
- Validates and normalizes the data
- Uploads data directly to Google BigQuery using MERGE (upsert) strategy
- Runs as a Google Cloud Function triggered by Cloud Scheduler
- Tracks attendance/confirmations for events and courses from January 2021 onward
- Includes a 7-day buffer to capture recent event modifications

## Architecture

```
Cloud Scheduler (HTTP Trigger)
    ↓
Cloud Functions (main.py)
    ↓
Data Extraction & Processing
    ↓
Validation Phase (all tables)
    ↓
Upload Phase (MERGE/upsert)
    ↓
Google BigQuery
```

## Setup

### Prerequisites

- Python 3.13+
- Google Cloud Project with BigQuery enabled
- MyClub API token

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ehms_mc_api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.template .env
```

Edit `.env` with your actual credentials and configuration (see [Configuration](#configuration) below)

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### Required Variables

- **`MC_TOKEN`** - Your MyClub API authentication token
- **`GCP_PROJECT_ID`** - Your Google Cloud Project ID (e.g., `ehms-424721`)
- **`BIGQUERY_DATASET_ID`** - BigQuery dataset name (e.g., `ehms_myclub`)

#### Optional Variables

- **`GOOGLE_CREDENTIALS_PATH`** - Path to GCP service account JSON file for authentication
- **`SILENT_MODE`** - Suppress informational output (useful for deployment). Valid values: `true`, `1`, `yes`. When enabled, only errors are logged to stderr.

### Authentication Methods

#### Method 1: Default Application Credentials (Recommended for Development)

If `GOOGLE_CREDENTIALS_PATH` is not set, the application uses Google's default application credentials chain:

```env
GCP_PROJECT_ID="your-gcp-project-id"
BIGQUERY_DATASET_ID="ehms_myclub"
```

Set up default credentials:
```bash
gcloud auth application-default login
```

#### Method 2: Service Account Credentials (Recommended for Production)

If you have a service account key file, set the path in your `.env`:

```env
GCP_PROJECT_ID="your-gcp-project-id"
BIGQUERY_DATASET_ID="ehms_myclub"
GOOGLE_CREDENTIALS_PATH="/path/to/service-account-key.json"
```

To create a service account:
1. Go to Google Cloud Console
2. Navigate to Service Accounts
3. Create a new service account
4. Grant it BigQuery Admin role (or at minimum: BigQuery Data Editor + BigQuery Job User)
5. Create and download a JSON key file
6. Set `GOOGLE_CREDENTIALS_PATH` to the file location

## Usage

### Local Development

#### Run Once

To fetch and upload data for a 60-day interval:

```bash
python src/initialise.py
```

#### Run with Custom Interval

To fetch data for a different number of days:

```bash
python src/initialise.py 30  # 30-day interval
```

Or in Python:

```python
from src import initialise
initialise.run(interval=30)  # 30-day interval
```

#### Enable Silent Mode

For deployment or when you don't need verbose output:

```bash
SILENT_MODE=true python src/initialise.py
```

### Cloud Functions Deployment

The application is designed to run as a Google Cloud Function:

#### Deploy to Cloud Functions

```bash
gcloud functions deploy run_pipeline \
  --runtime python313 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point run_pipeline \
  --set-env-vars MC_TOKEN=your-token,GCP_PROJECT_ID=your-project,BIGQUERY_DATASET_ID=ehms_myclub,SILENT_MODE=true
```

#### Trigger via HTTP

```bash
curl https://REGION-PROJECT_ID.cloudfunctions.net/run_pipeline
```

With custom interval:

```bash
curl "https://REGION-PROJECT_ID.cloudfunctions.net/run_pipeline?interval=30"
```

#### Schedule with Cloud Scheduler

Create a Cloud Scheduler job to run the pipeline periodically:

```bash
gcloud scheduler jobs create http myclub-weekly-sync \
  --schedule="0 0 * * 1" \
  --uri="https://REGION-PROJECT_ID.cloudfunctions.net/run_pipeline" \
  --http-method=GET \
  --time-zone="Europe/Helsinki"
```

This runs the pipeline every Monday at 00:00 (Helsinki time).

## Data Structure

### BigQuery Tables

The following tables are created and populated in BigQuery:

#### `categories`
- `category_id` (INTEGER, PRIMARY KEY)
- `category_name` (STRING)

#### `courses`
- `course_id` (INTEGER, PRIMARY KEY)
- `course_name` (STRING)
- `starts_at` (TIMESTAMP)
- `ends_at` (TIMESTAMP)
- `group_id` (INTEGER)

#### `events`
- `event_id` (INTEGER, PRIMARY KEY)
- `event_name` (STRING)
- `starts_at` (TIMESTAMP)
- `ends_at` (TIMESTAMP)
- `event_category_id` (INTEGER)
- `group_id` (INTEGER)
- `venue_id` (INTEGER)
- `course_id` (INTEGER)

#### `groups`
- `group_id` (INTEGER, PRIMARY KEY)
- `group_name` (STRING)

#### `members`
- `member_id` (INTEGER, PRIMARY KEY)
- `active` (STRING)
- `birthday` (DATE)
- `country` (STRING)
- `city` (STRING)
- `gender` (STRING)
- `member_since` (DATE)

#### `memberships`
- `member_id` (INTEGER, PRIMARY KEY, COMPOSITE)
- `group_id` (INTEGER, PRIMARY KEY, COMPOSITE)

#### `presences` (Core Data)
- `member_id` (INTEGER, PRIMARY KEY, COMPOSITE)
- `event_id` (INTEGER, PRIMARY KEY, COMPOSITE)
- `confirmed` (STRING)

## Data Pipeline Details

### Date Range Logic

The pipeline automatically calculates the date range to fetch:

1. **First run**: Starts from January 1, 2021
2. **Subsequent runs**: Starts from the most recent event date in BigQuery **minus 7 days** (buffer period)
3. **End date**: 8 days before today (to allow for late confirmations)
4. **Interval**: Fetches in 60-day chunks by default

The **7-day buffer** ensures that:
- Recent event modifications are captured (e.g., late confirmations, attendance updates)
- Data remains consistent even when events are edited after the initial sync
- No data is missed due to timing issues

This approach ensures:
- All historical data is captured
- Late confirmations are captured (8-day lag)
- Recent modifications are re-synced via the 7-day buffer
- Data is fetched incrementally to avoid timeouts

### Data Validation and Upload Strategy

#### Two-Phase Upload Process

The application uses a robust two-phase approach:

**Phase 1: Validation**
- All tables are validated **before** any data is inserted
- Creates temporary tables to test data insertion
- Checks for schema compatibility, data type errors, and constraint violations
- If **any** table fails validation, the entire upload is aborted
- This prevents partial uploads that could leave the database inconsistent

**Phase 2: MERGE (Upsert)**
- Uses BigQuery's MERGE statement for all tables
- **Updates** existing records (matched by primary key)
- **Inserts** new records
- No duplicates are created
- Perfect for handling the 7-day buffer overlap

#### Data Safety

- Uses parameterized queries to prevent SQL injection
- All table names are validated against an allowlist
- BigQuery handles data type conversions automatically
- Errors are logged to stderr even in silent mode

## Project Structure

```
ehms_mc_api/
├── main.py                     # Cloud Functions entry point (HTTP & CloudEvent triggers)
├── src/
│   ├── initialise.py           # Main pipeline orchestration
│   ├── logger.py               # Centralized logging with silent mode support
│   ├── bigquery_upload.py      # BigQuery integration (MERGE/upsert, validation)
│   ├── get_all_presences.py    # Aggregates all data across date range
│   ├── event.py                # Extracts event details and presences
│   ├── course.py               # Extracts course details
│   ├── member.py               # Extracts member details and memberships
│   ├── events_in_group.py      # Queries events for a group
│   ├── courses_in_group.py     # Queries courses for a group
│   ├── groups.py               # Fetches groups/organizations
│   ├── categories.py           # Fetches event categories
│   ├── venues.py               # Fetches venue information
│   ├── upcoming_events.py      # Fetches upcoming events in non-EHMS venues
│   └── truncate_tables.py      # Utility to truncate all BigQuery tables
├── requirements.txt            # Python dependencies
├── .env.template               # Environment configuration template
├── .env                        # Your environment configuration (not in git)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Development

### Key Modules

- **`main.py`**: Cloud Functions entry points
  - `run_pipeline(request)` - HTTP trigger with optional interval parameter
  - `run_pipeline_cloud_event(cloud_event)` - CloudEvent trigger
  - Error handling and status reporting

- **`logger.py`**: Centralized logging
  - `log()` - Informational messages (respects SILENT_MODE)
  - `error()` - Error messages (always logged to stderr)
  - Configurable via `SILENT_MODE` environment variable

- **`bigquery_upload.py`**: BigQuery operations
  - Two-phase validation and upload process
  - MERGE (upsert) strategy for all tables
  - Temporary table validation
  - Client initialization with configurable credentials
  - Dataset and table creation with schema management
  - Comprehensive error handling and reporting

- **`initialise.py`**: Pipeline orchestration
  - Calculates date range with 7-day buffer
  - Fetches data from MyClub API
  - Prepares data for BigQuery upload
  - Calls validation and upload functions

- **`get_all_presences.py`**: Data aggregation
  - Fetches all presences, events, courses, members across groups
  - Progress bars for tracking (respects SILENT_MODE)
  - Coordinates parallel API calls

### Utility Scripts

- **`truncate_tables.py`**: Database maintenance
  - Safely truncates all BigQuery tables
  - Requires explicit confirmation
  - Useful for testing or complete data refresh

## Troubleshooting

### Authentication Errors

**Error**: `google.auth.exceptions.DefaultCredentialsError`

**Solution**: Set up credentials using one of these methods:
1. Run `gcloud auth application-default login`
2. Set `GOOGLE_CREDENTIALS_PATH` to a service account key file

### BigQuery Permission Errors

**Error**: `google.cloud.exceptions.Forbidden`

**Solution**: Ensure your service account has these roles:
- BigQuery Data Editor
- BigQuery Job User

### Missing Data

**Error**: Tables are created but no data is inserted

**Check**:
1. MyClub API token is valid
2. Date range has data available
3. Check BigQuery logs in Google Cloud Console

### Validation Errors

**Error**: `Validation failed for X table(s). No data was inserted to maintain consistency.`

**What it means**:
- The validation phase detected data incompatibility issues
- **No data was inserted** - your database remains consistent
- Check the detailed error messages to see which fields/rows failed

**Common causes**:
- Schema changes in MyClub API
- Unexpected null values in required fields
- Data type mismatches

**Solution**:
1. Check the error output for specific field/row issues
2. Verify the MyClub API response format hasn't changed
3. Check BigQuery table schemas match expectations

### Silent Mode Issues

**Issue**: No output when running locally

**Solution**:
- Check if `SILENT_MODE` is set in your `.env` file
- Unset or set to `false` to see output: `SILENT_MODE=false`
- Errors are always logged even in silent mode (check stderr)

## Dependencies

- `requests` - HTTP client for MyClub API calls
- `python-dotenv` - Environment variable management
- `google-cloud-bigquery` - BigQuery client library for data upload
- `functions-framework` - Framework for running Cloud Functions locally and in production

## License

(Add your license here)

## Support

For issues, questions, or contributions, please create an issue in the repository.
