import datetime

import get_all_presences
import categories
import groups
import bigquery_upload

import os


def run(interval=60):
    """
    Call the API and populate BigQuery directly, using the specified interval.
    If no interval is explicitly specified, an interval of 60 days is used.
    """

    date = "2021-01-01T00:00:00.000"
    start = datetime.datetime.strptime(
        date, "%Y-%m-%dT%H:%M:%S.%f"
    ).date()  # convert it to date

    # Get the most recent date from BigQuery
    client = bigquery_upload.initialize_bigquery_client()
    most_recent = bigquery_upload.get_most_recent_date(client)
    if most_recent:
        # Parse the date string and convert to date object
        most_recent_clean = most_recent[:-4]  # Remove milliseconds and Z if present
        most_recent_date = datetime.datetime.strptime(
            most_recent_clean, "%Y-%m-%dT%H:%M:%S"
        ).date()
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

    # Helper function to clean data (replace single quotes with question marks)
    def clean_data(data_list):
        for i in range(len(data_list)):
            for k, v in data_list[i].items():
                data_list[i][k] = str(v).replace("'", "?")
        return data_list

    # Clean all data
    _categories = clean_data(_categories)
    courses = clean_data(courses)
    events = clean_data(events)
    members = clean_data(members)
    memberships = clean_data(memberships)
    _groups = clean_data(_groups)
    presences = clean_data(presences)

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
    run()
