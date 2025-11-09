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
            bigquery.SchemaField("event_category_id", "INTEGER"),
            bigquery.SchemaField("group_id", "INTEGER"),
            bigquery.SchemaField("venue_id", "INTEGER"),
            bigquery.SchemaField("course_id", "INTEGER"),
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

    try:
        client.get_table(table_ref)
        print(f"Table {table_name} already exists.")
        return
    except NotFound:
        schema = get_table_schema(table_name)
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table)
        print(f"Created table {table_name}")


def insert_rows(client, table_name, rows):
    """Insert rows into a BigQuery table."""
    if not rows:
        print(f"No entries for {table_name}")
        return

    dataset_ref = client.dataset(BIGQUERY_DATASET_ID)
    table_ref = dataset_ref.table(table_name)
    table = client.get_table(table_ref)

    # Convert list of dicts to list of tuples in the correct order
    errors = client.insert_rows_json(table_ref, rows)

    if errors:
        print(f"Errors inserting rows into {table_name}:")
        for error in errors:
            print(error)
    else:
        print(f"Successfully inserted {len(rows)} rows into {table_name}")


def upload_all_tables(data_dict):
    """
    Upload all tables to BigQuery.

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
    for table_name in data_dict.keys():
        create_table_if_not_exists(client, table_name)

    # Insert rows
    for table_name, rows in data_dict.items():
        insert_rows(client, table_name, rows)


if __name__ == "__main__":
    # Test the BigQuery connection
    client = initialize_bigquery_client()
    print(f"Connected to GCP project: {GCP_PROJECT_ID}")
    print(f"Using dataset: {BIGQUERY_DATASET_ID}")
