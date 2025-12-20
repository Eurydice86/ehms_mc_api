"""
Script to truncate all BigQuery tables used by the EHMS MyClub API.

This will delete all data from the following tables:
- categories
- courses
- events
- groups
- members
- memberships
- presences

Use with caution - this operation cannot be undone!
"""

import bigquery_upload
from logger import log, error


TABLES_TO_TRUNCATE = [
    "categories",
    "courses",
    "events",
    "groups",
    "members",
    "memberships",
    "presences",
]


def truncate_all_tables():
    """Truncate all data tables in BigQuery."""
    client = bigquery_upload.initialize_bigquery_client()

    log("WARNING: This will delete ALL data from the following tables:")
    for table_name in TABLES_TO_TRUNCATE:
        log(f"  - {table_name}")

    confirmation = input("\nType 'DELETE ALL DATA' to confirm: ")

    if confirmation != "DELETE ALL DATA":
        log("Aborted - no data was deleted")
        return

    log("\nTruncating tables...")

    for idx, table_name in enumerate(TABLES_TO_TRUNCATE, 1):
        table_ref = f"{bigquery_upload.GCP_PROJECT_ID}.{bigquery_upload.BIGQUERY_DATASET_ID}.{table_name}"

        try:
            query = f"TRUNCATE TABLE `{table_ref}`"
            query_job = client.query(query)
            query_job.result()  # Wait for completion
            log(f"  [{idx}/{len(TABLES_TO_TRUNCATE)}] ✓ Truncated {table_name}")
        except Exception as e:
            error(f"  [{idx}/{len(TABLES_TO_TRUNCATE)}] ✗ Error truncating {table_name}: {e}")

    log("\nTruncation completed!")


if __name__ == "__main__":
    truncate_all_tables()
