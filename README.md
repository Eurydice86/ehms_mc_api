# EHMS MyClub API

An automated data extraction and synchronization system that fetches member, event, course, and attendance data from the MyClub API and uploads it directly to Google BigQuery.

## Overview

This application:
- Fetches member, event, course, and attendance data from the MyClub API
- Cleans and normalizes the data
- Uploads the data directly to Google BigQuery
- Runs periodically (weekly on Mondays) to keep data up-to-date
- Tracks attendance/confirmations for events and courses from January 2021 onward

## Architecture

```
MyClub API
    ↓
Data Extraction & Processing
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
cp .env.example .env
```

Edit `.env` with your configuration (see [Configuration](#configuration) below)

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

#### Required Variables

- **`MC_TOKEN`** - Your MyClub API authentication token
- **`GCP_PROJECT_ID`** - Your Google Cloud Project ID (e.g., `ehms-424721`)
- **`BIGQUERY_DATASET_ID`** - BigQuery dataset name (e.g., `ehms_myclub`)

#### Optional Variables

- **`GOOGLE_CREDENTIALS_PATH`** - Path to GCP service account JSON file for authentication

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

### Run Once

To fetch and upload data for a 60-day interval:

```bash
python src/initialise.py
```

### Run with Custom Interval

To fetch data for a different number of days:

```python
from src import initialise
initialise.run(interval=30)  # 30-day interval
```

### Run on Schedule

To run the data pipeline weekly (every Monday at 00:00):

```bash
python src/scheduling.py
```

This will continuously monitor and execute the pipeline on schedule.

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
2. **Subsequent runs**: Starts from the last event date found in the database
3. **End date**: 8 days before today (to allow for late confirmations)
4. **Interval**: Fetches in 60-day chunks by default

This approach ensures:
- All historical data is captured
- Late confirmations are captured (8-day lag)
- Data is fetched incrementally to avoid timeouts

### Data Cleaning

Before uploading to BigQuery, the application:
- Replaces single quotes with `?` (to avoid SQL injection concerns)
- Validates field types
- Handles null/empty values appropriately

## Project Structure

```
ehms_mc_api/
├── src/
│   ├── initialise.py           # Main entry point - orchestrates the pipeline
│   ├── scheduling.py           # Scheduler for periodic execution
│   ├── bigquery_upload.py       # BigQuery integration and uploads
│   ├── get_all_presences.py     # Aggregates all data across date range
│   ├── event.py                # Extracts event details and presences
│   ├── course.py               # Extracts course details
│   ├── member.py               # Extracts member details
│   ├── events_in_group.py       # Queries events for a group
│   ├── courses_in_group.py      # Queries courses for a group
│   ├── groups.py               # Fetches groups/organizations
│   ├── categories.py           # Fetches event categories
│   ├── venues.py               # Fetches venue information
│   └── db_sql.py               # Legacy database utilities
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment configuration
├── .env                        # Environment configuration (not in git)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Development

### Key Modules

- **`bigquery_upload.py`**: Handles all BigQuery operations
  - Client initialization with configurable credentials
  - Dataset and table creation
  - Row insertion with error handling

- **`initialise.py`**: Main orchestration
  - Fetches data from MyClub API
  - Cleans and normalizes data
  - Uploads to BigQuery

- **`scheduling.py`**: Periodic execution
  - Runs `initialise.py` on a schedule
  - Currently configured for Mondays at 00:00

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

## Dependencies

- `requests` - HTTP client for API calls
- `python-dotenv` - Environment variable management
- `schedule` - Job scheduling library
- `google-cloud-bigquery` - BigQuery client library
- `google-cloud-storage` - Cloud Storage client (legacy, can be removed)

## License

(Add your license here)

## Support

For issues, questions, or contributions, please create an issue in the repository.
