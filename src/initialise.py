import datetime
import argparse

import get_all_presences
import categories
import groups
import bigquery_upload

import os


def run(interval=60):
    """
    Main pipeline function to fetch data from MyClub API and upload to BigQuery.

    This function:
    1. Determines the date range (from most recent BigQuery data - 7 days buffer)
    2. Fetches all data (presences, events, courses, members, etc.) from MyClub API
    3. Uploads data directly to BigQuery using MERGE (upsert) strategy

    The 7-day buffer ensures that any modifications to recent events are captured.

    Args:
        interval (int): Number of days to fetch from the start date (default: 60)

    Raises:
        Exception: If BigQuery upload fails or API calls fail
    """

    date = "2021-01-01T00:00:00.000"
    start = datetime.datetime.strptime(
        date, "%Y-%m-%dT%H:%M:%S.%f"
    ).date()  # convert it to date

    # Get the most recent date from BigQuery
    client = bigquery_upload.initialize_bigquery_client()
    most_recent = bigquery_upload.get_most_recent_date(client)
    if most_recent:
        # Parse the ISO format datetime string (handles timezone automatically)
        most_recent_date = datetime.datetime.fromisoformat(most_recent).date()
        # Add 7-day buffer to catch any modifications to recent events
        start = most_recent_date - datetime.timedelta(days=7)

    # either <interval> days after start or a week ago
    # (people still sometimes go back to confirm presences they forgot)
    end = min(
        start + datetime.timedelta(days=interval),
        (datetime.datetime.now() - datetime.timedelta(days=8)).date(),
    )

    presences, events, courses, members, memberships = (
        get_all_presences.get_all_presences_in_date_range(start, end)
    )

    _categories = categories.categories()
    _groups = groups.get_group_ids()

    # Note: No data cleaning needed - BigQuery handles all data types properly
    # and parameterized queries in MERGE statement prevent SQL injection

    # Prepare data dictionary for BigQuery upload
    data_to_upload = {
        "categories": _categories,
        "courses": courses,
        "events": events,
        "groups": _groups,
        "members": members,
        "memberships": memberships,
        "presences": presences,
    }

    # Upload directly to BigQuery
    print("Uploading to BigQuery")
    bigquery_upload.upload_all_tables(data_to_upload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch data from MyClub API and upload to BigQuery"
    )
    parser.add_argument(
        "interval",
        type=int,
        nargs="?",
        default=60,
        help="Number of days to fetch from the start date (default: 60)"
    )
    args = parser.parse_args()

    print(f"Running with interval: {args.interval} days")
    run(interval=args.interval)
