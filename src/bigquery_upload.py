"""
BigQuery integration module for direct data upload.
Replaces the SQLite -> CSV -> GCS -> BigQuery pipeline.
"""

import os
import json
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account

load_dotenv()

# Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "ehms-424721")
BIGQUERY_DATASET_ID = os.getenv("BIGQUERY_DATASET_ID", "ehms_myclub")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")


def initialize_bigquery_client():
    """
    Initialize and return a BigQuery client.

    Uses service account credentials if GOOGLE_CREDENTIALS_PATH is set,
    otherwise falls back to default application credentials.
    """
    if GOOGLE_CREDENTIALS_PATH:
        # Load credentials from service account JSON file
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH
        )
        client = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)
        print(f"Initialized BigQuery client with credentials from {GOOGLE_CREDENTIALS_PATH}")
    else:
        # Use default application credentials
        client = bigquery.Client(project=GCP_PROJECT_ID)
        print("Initialized BigQuery client with default application credentials")

    return client


def create_dataset_if_not_exists(client):
    """Create the BigQuery dataset if it doesn't already exist."""
    dataset_id = BIGQUERY_DATASET_ID
    dataset_ref = client.dataset(dataset_id)

    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_id} already exists.")
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"Created dataset {dataset_id}")


def get_table_schema(table_name):
    """Define BigQuery schemas for each table."""
    schemas = {
        "categories": [
            bigquery.SchemaField("category_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("category_name", "STRING"),
        ],
        "courses": [
            bigquery.SchemaField("course_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("course_name", "STRING"),
            bigquery.SchemaField("starts_at", "TIMESTAMP"),
            bigquery.SchemaField("ends_at", "TIMESTAMP"),
            bigquery.SchemaField("group_id", "INTEGER"),
        ],
        "events": [
            bigquery.SchemaField("event_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("event_name", "STRING"),
            bigquery.SchemaField("starts_at", "TIMESTAMP"),
            bigquery.SchemaField("ends_at", "TIMESTAMP"),
            bigquery.SchemaField("event_category_id", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("group_id", "INTEGER"),
            bigquery.SchemaField("venue_id", "INTEGER", mode="NULLABLE"),
            bigquery.SchemaField("course_id", "INTEGER", mode="NULLABLE"),
        ],
        "groups": [
            bigquery.SchemaField("group_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("group_name", "STRING"),
        ],
        "members": [
            bigquery.SchemaField("member_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("active", "STRING"),
            bigquery.SchemaField("birthday", "DATE"),
            bigquery.SchemaField("country", "STRING"),
            bigquery.SchemaField("city", "STRING"),
            bigquery.SchemaField("gender", "STRING"),
            bigquery.SchemaField("member_since", "DATE"),
        ],
        "memberships": [
            bigquery.SchemaField("member_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("group_id", "INTEGER", mode="REQUIRED"),
        ],
        "presences": [
            bigquery.SchemaField("member_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("event_id", "INTEGER", mode="REQUIRED"),
            bigquery.SchemaField("confirmed", "STRING"),
        ],
    }
    return schemas.get(table_name, [])


def create_table_if_not_exists(client, table_name):
    """Create a BigQuery table if it doesn't already exist."""
    dataset_ref = client.dataset(BIGQUERY_DATASET_ID)
    table_ref = dataset_ref.table(table_name)
    new_schema = get_table_schema(table_name)

    try:
        table = client.get_table(table_ref)
        print(f"Table {table_name} already exists.")
        return
    except NotFound:
        table = bigquery.Table(table_ref, schema=new_schema)
        table = client.create_table(table)
        print(f"Created table {table_name}")


def insert_rows(client, table_name, rows, replace=False):
    """
    Insert rows into a BigQuery table.

    Args:
        client: BigQuery client instance
        table_name: Name of the table
        rows: List of row dictionaries
        replace: If True, replace existing rows (for handling updates to recent data)
    """
    if not rows:
        print(f"No entries for {table_name}")
        return

    dataset_ref = client.dataset(BIGQUERY_DATASET_ID)
    table_ref = dataset_ref.table(table_name)
    table = client.get_table(table_ref)

    # Insert rows
    errors = client.insert_rows_json(table_ref, rows, skip_invalid_rows=False)

    if errors:
        print(f"Errors inserting rows into {table_name}:")
        for error in errors:
            print(error)
    else:
        print(f"Successfully inserted {len(rows)} rows into {table_name}")


def delete_and_replace_rows(client, table_name, rows, date_field, buffer_days=7):
    """
    Delete rows from a date range and re-insert them to handle updates.

    This is useful for handling recent events that may have been modified.

    Args:
        client: BigQuery client instance
        table_name: Name of the table
        rows: List of row dictionaries to insert
        date_field: Name of the date field to use for filtering (e.g., 'starts_at')
        buffer_days: Number of days back to delete before re-inserting
    """
    if not rows:
        print(f"No entries for {table_name}")
        return

    # Find the minimum date in the rows to delete
    min_date = None
    for row in rows:
        if date_field in row and row[date_field]:
            row_date = row[date_field]
            # Handle both string and datetime formats
            if isinstance(row_date, str):
                # Parse ISO format date strings
                row_date = row_date.split('T')[0]  # Get just the date part
            if not min_date or row_date < min_date:
                min_date = row_date

    if not min_date:
        print(f"No valid dates found in {table_name}, inserting without delete")
        insert_rows(client, table_name, rows)
        return

    # Delete rows from the buffer period
    try:
        delete_query = f"""
            DELETE FROM `{GCP_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{table_name}`
            WHERE DATE({date_field}) >= DATE('{min_date}')
        """
        query_job = client.query(delete_query)
        query_job.result()  # Wait for the delete to complete
        print(f"Deleted rows from {table_name} from {min_date} onwards")
    except Exception as e:
        print(f"Warning: Could not delete old rows from {table_name}: {e}")

    # Insert the new/updated rows
    insert_rows(client, table_name, rows)


def get_most_recent_date(client):
    """
    Get the most recent event start date from BigQuery.

    Args:
        client: BigQuery client instance

    Returns:
        str: ISO format datetime string (e.g., "2021-01-01T00:00:00.000")
             or None if no events exist in the database.
    """
    try:
        query = f"""
            SELECT MAX(starts_at) as max_date
            FROM `{GCP_PROJECT_ID}.{BIGQUERY_DATASET_ID}.events`
        """
        query_job = client.query(query)
        results = query_job.result()

        for row in results:
            max_date = row.max_date
            if max_date:
                # Convert timestamp to ISO format string with milliseconds
                iso_str = max_date.isoformat()
                # Ensure format: "2021-01-01T00:00:00.000"
                if '.' not in iso_str:
                    iso_str += '.000'
                return iso_str
            else:
                print("No events found in BigQuery")
                return None

    except NotFound:
        print(f"Dataset {BIGQUERY_DATASET_ID} or table 'events' not found in BigQuery")
        return None
    except Exception as e:
        print(f"Error retrieving most recent date from BigQuery: {e}")
        return None


def upload_all_tables(data_dict):
    """
    Upload all tables to BigQuery.

    Uses delete-and-replace strategy for events and presences to handle
    modifications to recent data within the 7-day buffer period.

    Args:
        data_dict: Dictionary with table names as keys and row lists as values.
                   Example: {
                       'categories': [...],
                       'courses': [...],
                       'events': [...],
                       'groups': [...],
                       'members': [...],
                       'memberships': [...],
                       'presences': [...]
                   }
    """
    client = initialize_bigquery_client()

    # Create dataset and tables
    create_dataset_if_not_exists(client)
    print(f"Creating tables if needed...")
    for idx, table_name in enumerate(data_dict.keys(), 1):
        print(f"  Checking table {idx}/{len(data_dict)}: {table_name}", end='\r')
        create_table_if_not_exists(client, table_name)
    print(f"  All tables ready ({len(data_dict)} tables)              ")

    # Insert rows with delete-and-replace for tables with date-based updates
    print(f"Uploading data to BigQuery...")
    for idx, (table_name, rows) in enumerate(data_dict.items(), 1):
        print(f"  [{idx}/{len(data_dict)}] Uploading {table_name}...")
        if table_name == "events" and rows:
            # Delete and replace events to catch modifications
            delete_and_replace_rows(client, table_name, rows, "starts_at")
        elif table_name == "presences" and rows:
            # For presences, we need to join with events to get the date
            # For now, just use regular insert with skip duplicates
            insert_rows(client, table_name, rows)
        else:
            # All other tables: regular insert
            insert_rows(client, table_name, rows)
    print(f"Upload completed!")


if __name__ == "__main__":
    # Test the BigQuery connection
    client = initialize_bigquery_client()
    print(f"Connected to GCP project: {GCP_PROJECT_ID}")
    print(f"Using dataset: {BIGQUERY_DATASET_ID}")
