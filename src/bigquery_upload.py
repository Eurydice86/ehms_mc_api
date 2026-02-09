"""
BigQuery integration module for direct data upload.
Replaces the SQLite -> CSV -> GCS -> BigQuery pipeline.
"""

import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account
from logger import log, error

load_dotenv()


def progress_bar(current, total, width=30):
    """Generate a progress bar string."""
    percentage = current / total if total > 0 else 0
    filled = int(width * percentage)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {current}/{total}"

# Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "ehms-424721")
BIGQUERY_DATASET_ID = os.getenv("BIGQUERY_DATASET_ID", "ehms_myclub")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Allowed table names for security
ALLOWED_TABLES = {"categories", "courses", "events", "groups", "members", "memberships", "presences"}


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
    else:
        # Use default application credentials
        client = bigquery.Client(project=GCP_PROJECT_ID)

    return client


def create_dataset_if_not_exists(client):
    """Create the BigQuery dataset if it doesn't already exist."""
    dataset_id = BIGQUERY_DATASET_ID
    dataset_ref = client.dataset(dataset_id)

    try:
        client.get_dataset(dataset_ref)
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        dataset = client.create_dataset(dataset, timeout=30)
        log(f"Created dataset {dataset_id}")


def get_table_schema(table_name):
    """Define BigQuery schemas for each table."""
    schemas = {
        "categories": [
            bigquery.SchemaField("category_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("category_name", "STRING"),
        ],
        "courses": [
            bigquery.SchemaField("course_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("course_name", "STRING"),
            bigquery.SchemaField("starts_at", "TIMESTAMP"),
            bigquery.SchemaField("ends_at", "TIMESTAMP"),
            bigquery.SchemaField("group_id", "STRING"),
        ],
        "events": [
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("event_name", "STRING"),
            bigquery.SchemaField("starts_at", "TIMESTAMP"),
            bigquery.SchemaField("ends_at", "TIMESTAMP"),
            bigquery.SchemaField("event_category_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("group_id", "STRING"),
            bigquery.SchemaField("venue_id", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("course_id", "STRING", mode="NULLABLE"),
        ],
        "groups": [
            bigquery.SchemaField("group_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("group_name", "STRING"),
        ],
        "members": [
            bigquery.SchemaField("member_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("active", "BOOLEAN"),
            bigquery.SchemaField("birthday", "DATE"),
            bigquery.SchemaField("country", "STRING"),
            bigquery.SchemaField("city", "STRING"),
            bigquery.SchemaField("gender", "STRING"),
            bigquery.SchemaField("member_since", "DATE"),
        ],
        "memberships": [
            bigquery.SchemaField("member_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("group_id", "STRING", mode="REQUIRED"),
        ],
        "presences": [
            bigquery.SchemaField("member_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("confirmed", "BOOLEAN"),
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
        return
    except NotFound:
        table = bigquery.Table(table_ref, schema=new_schema)
        table = client.create_table(table)
        log(f"Created table {table_name}")


def get_primary_keys(table_name):
    """Return the primary key field(s) for each table."""
    primary_keys = {
        "categories": ["category_id"],
        "courses": ["course_id"],
        "events": ["event_id"],
        "groups": ["group_id"],
        "members": ["member_id"],
        "memberships": ["member_id", "group_id"],
        "presences": ["member_id", "event_id"],
    }
    return primary_keys.get(table_name, [])


def validate_rows(client, table_name, rows):
    """
    Validate that rows can be inserted into a BigQuery table without actually inserting them.

    Creates a temporary table and attempts to insert the rows, then immediately deletes the table.
    This allows us to catch validation errors before committing to the actual merge operation.

    Args:
        client: BigQuery client instance
        table_name: Name of the table
        rows: List of row dictionaries

    Returns:
        True if validation successful

    Raises:
        RuntimeError: If validation fails with details about the errors
    """
    if not rows:
        return True

    # Create a temporary validation table
    import uuid
    validation_table_name = f"{table_name}_validation_{uuid.uuid4().hex[:8]}"
    dataset_ref = client.dataset(BIGQUERY_DATASET_ID)
    validation_table_ref = dataset_ref.table(validation_table_name)

    # Get schema for the table
    schema = get_table_schema(table_name)

    validation_table_created = False
    try:
        # Create temporary validation table
        validation_table = bigquery.Table(validation_table_ref, schema=schema)
        validation_table = client.create_table(validation_table)
        validation_table_created = True

        # Attempt to insert data
        errors = client.insert_rows_json(validation_table_ref, rows, skip_invalid_rows=False)
        if errors:
            error_msg = f"Validation failed for {table_name}:\n"
            for error in errors:
                error_msg += f"  Row index: {error.get('index', 'unknown')}\n"
                for err in error.get('errors', []):
                    error_msg += f"    - {err.get('reason', 'unknown')}: {err.get('message', 'no message')}\n"
                    error_msg += f"      Location: {err.get('location', 'unknown')}\n"
            raise RuntimeError(error_msg)

        return True

    finally:
        # Clean up validation table
        if validation_table_created:
            try:
                client.delete_table(validation_table_ref)
            except NotFound:
                pass
            except Exception as e:
                log(f"Warning: Could not delete validation table {validation_table_name}: {e}")


def merge_rows(client, table_name, rows):
    """
    Merge rows into a BigQuery table using MERGE statement.

    This performs an upsert operation: inserts new rows and updates existing ones
    based on the primary key(s) for the table.

    Args:
        client: BigQuery client instance
        table_name: Name of the table
        rows: List of row dictionaries
    """
    # Validate table name for security
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}. Allowed tables: {ALLOWED_TABLES}")

    if not rows:
        log(f"No entries for {table_name}")
        return

    primary_keys = get_primary_keys(table_name)
    if not primary_keys:
        log(f"Warning: No primary keys defined for {table_name}, using insert_rows instead")
        insert_rows(client, table_name, rows)
        return

    # Create a temporary table name with unique suffix to avoid collisions
    import uuid
    temp_table_name = f"{table_name}_temp_{uuid.uuid4().hex[:8]}"
    dataset_ref = client.dataset(BIGQUERY_DATASET_ID)
    temp_table_ref = dataset_ref.table(temp_table_name)

    # Get schema for the table
    schema = get_table_schema(table_name)

    temp_table_created = False
    try:
        # Create temporary table
        temp_table = bigquery.Table(temp_table_ref, schema=schema)
        temp_table = client.create_table(temp_table)
        temp_table_created = True

        # Insert data into temporary table
        errors = client.insert_rows_json(temp_table_ref, rows, skip_invalid_rows=False)
        if errors:
            error(f"\nErrors inserting rows into temp table {temp_table_name}:")
            for err_item in errors:
                error(f"  Row index: {err_item.get('index', 'unknown')}")
                for err in err_item.get('errors', []):
                    error(f"    - {err.get('reason', 'unknown')}: {err.get('message', 'no message')}")
                    error(f"      Location: {err.get('location', 'unknown')}")
            raise RuntimeError(f"Failed to insert rows into {temp_table_name}")

        # Build MERGE statement
        match_condition = " AND ".join([f"target.{key} = source.{key}" for key in primary_keys])

        # Get all field names from schema
        all_fields = [field.name for field in schema]

        # Build UPDATE SET clause (update all fields except primary keys)
        update_fields = [f for f in all_fields if f not in primary_keys]

        # Build INSERT clause
        insert_fields = ", ".join(all_fields)
        insert_values = ", ".join([f"source.{field}" for field in all_fields])

        # Build MERGE query - handle edge case where there are no non-PK fields to update
        if not update_fields:
            # If all fields are primary keys, only INSERT (no UPDATE needed)
            merge_query = f"""
                MERGE `{GCP_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{table_name}` AS target
                USING `{GCP_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{temp_table_name}` AS source
                ON {match_condition}
                WHEN NOT MATCHED THEN
                    INSERT ({insert_fields})
                    VALUES ({insert_values})
            """
        else:
            # Normal case: both UPDATE and INSERT
            update_set = ", ".join([f"target.{field} = source.{field}" for field in update_fields])
            merge_query = f"""
                MERGE `{GCP_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{table_name}` AS target
                USING `{GCP_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{temp_table_name}` AS source
                ON {match_condition}
                WHEN MATCHED THEN
                    UPDATE SET {update_set}
                WHEN NOT MATCHED THEN
                    INSERT ({insert_fields})
                    VALUES ({insert_values})
            """

        # Execute MERGE
        query_job = client.query(merge_query)
        result = query_job.result()

        log(f" ✓ successfully merged {len(rows)} rows")

    except Exception as e:
        error(f"Error during merge operation for {table_name}: {e}")
        raise
    finally:
        # Clean up temporary table only if it was created
        if temp_table_created:
            try:
                client.delete_table(temp_table_ref)
            except NotFound:
                pass  # Already deleted, that's fine
            except Exception as e:
                log(f"Warning: Could not delete temp table {temp_table_name}: {e}")


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
        log(f"No entries for {table_name}")
        return

    dataset_ref = client.dataset(BIGQUERY_DATASET_ID)
    table_ref = dataset_ref.table(table_name)
    table = client.get_table(table_ref)

    # Insert rows
    errors = client.insert_rows_json(table_ref, rows, skip_invalid_rows=False)

    if errors:
        error(f"Errors inserting rows into {table_name}:")
        for err in errors:
            error(err)
    else:
        log(f"Successfully inserted {len(rows)} rows into {table_name}")


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
                iso_str = max_date.isoformat(timespec='milliseconds')
                return iso_str
            else:
                log("No events found in BigQuery")
                return None

    except NotFound:
        log(f"Dataset {BIGQUERY_DATASET_ID} or table 'events' not found in BigQuery")
        return None
    except Exception as e:
        error(f"Error retrieving most recent date from BigQuery: {e}")
        return None


def upload_all_tables(data_dict):
    """
    Upload all tables to BigQuery.

    Uses MERGE (upsert) strategy for all tables to handle updates to existing records.
    This ensures that:
    - New records are inserted
    - Existing records (matched by primary key) are updated
    - No duplicates are created

    Validation is performed on ALL tables before ANY data is inserted to prevent
    partial failures that would leave the database in an inconsistent state.

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
    log(f"Creating tables if needed...")
    for table_name in data_dict.keys():
        create_table_if_not_exists(client, table_name)
    log(f"  All tables ready ({len(data_dict)} tables)")

    # VALIDATION PHASE: Validate ALL tables before inserting ANY data
    log(f"Validating data for all tables...")
    validation_errors = []
    for idx, (table_name, rows) in enumerate(data_dict.items(), 1):
        if not rows:
            log(f"  [{idx}/{len(data_dict)}] Skipping validation for {table_name} (no data)")
            continue

        log(f"  [{idx}/{len(data_dict)}] Validating {table_name} ({len(rows)} rows)...", end='')
        try:
            validate_rows(client, table_name, rows)
            log(f" ✓ passed")
        except Exception as e:
            validation_errors.append((table_name, str(e)))
            log(f" ✗ FAILED")

    # If any validation failed, abort before inserting anything
    if validation_errors:
        error("\n" + "="*80)
        error("VALIDATION FAILED - No data was inserted")
        error("="*80)
        for table_name, err_msg in validation_errors:
            error(f"\n{table_name}:")
            error(err_msg)
        raise RuntimeError(f"Validation failed for {len(validation_errors)} table(s). No data was inserted to maintain consistency.")

    log(f"✓ All validations passed!\n")

    # INSERTION PHASE: Now that all validations passed, perform the actual merges
    log(f"Uploading data to BigQuery...")
    for idx, (table_name, rows) in enumerate(data_dict.items(), 1):
        log(f"  [{idx}/{len(data_dict)}] Uploading {table_name}...", end='', flush=True)
        merge_rows(client, table_name, rows)
    log(f"  Upload completed!")


if __name__ == "__main__":
    # Test the BigQuery connection
    client = initialize_bigquery_client()
    log(f"Connected to GCP project: {GCP_PROJECT_ID}")
    log(f"Using dataset: {BIGQUERY_DATASET_ID}")
