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

    # TODO: Get most recent date from BigQuery instead of SQLite
    # For now, we'll start from the beginning each time or you can manually set start date

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
