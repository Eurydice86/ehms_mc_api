import datetime

import get_all_presences
import db_sql
import categories
import groups

import copy_to_gstorage

import json

import os
import sqlite3


def run(interval=60):
    """
    Call the API and populate / append to the database, using the specified interval.
    If no interval is explicitly specified, an interval of 60 days is used.
    """

    if not os.path.exists("data"):
        os.makedirs("data")

    date = "2021-01-01T00:00:00.000"
    start = datetime.datetime.strptime(
        date, "%Y-%m-%dT%H:%M:%S.%f"
    ).date()  # convert it to date

    db_sql.initialise_db()
    dt = (
        db_sql.most_recent_date()
    )  # get the most recent date from the db (it returns a str)
    if dt:
        dt = dt[:-6]
        start = datetime.datetime.strptime(
            dt, "%Y-%m-%dT%H:%M:%S.%f"
        ).date()  # convert it to date

    # either <interval> days after start or a week ago (people still sometimes go back to confirm presences they forgot)
    end = min(
        start + datetime.timedelta(days=interval),
        (datetime.datetime.now() - datetime.timedelta(days=8)).date(),
    )

    presences, events, courses, members, memberships = (
        get_all_presences.get_all_presences_in_date_range(start, end)
    )

    _categories = categories.categories()
    _groups = groups.get_group_ids()

    # replacing single quotes with question marks
    for i in range(len(_categories)):
        for k, v in _categories[i].items():
            _categories[i][k] = str(v).replace("'", "?")

    for i in range(len(courses)):
        for k, v in courses[i].items():
            courses[i][k] = str(v).replace("'", "?")

    for i in range(len(events)):
        for k, v in events[i].items():
            events[i][k] = str(v).replace("'", "?")

    for i in range(len(members)):
        for k, v in members[i].items():
            members[i][k] = str(v).replace("'", "?")

    for i in range(len(memberships)):
        for k, v in memberships[i].items():
            memberships[i][k] = str(v).replace("'", "?")

    for i in range(len(_groups)):
        for k, v in _groups[i].items():
            _groups[i][k] = str(v).replace("'", "?")

    for i in range(len(presences)):
        for k, v in presences[i].items():
            presences[i][k] = str(v).replace("'", "?")

    db_sql.initialise_db()
    db_sql.add_rows("categories", _categories)
    db_sql.add_rows("courses", courses)
    db_sql.add_rows("events", events)
    db_sql.add_rows_replace("members", members)
    db_sql.add_rows("memberships", memberships)
    db_sql.add_rows("groups", _groups)
    db_sql.add_rows("presences", presences)


    print("Exporting to csv")
    db_sql.table_to_csv("categories")
    db_sql.table_to_csv("courses")
    db_sql.table_to_csv("events")
    db_sql.table_to_csv("members")
    db_sql.table_to_csv("memberships")
    db_sql.table_to_csv("groups")
    db_sql.table_to_csv("presences")

    print("Uploadind to GCS")
    copy_to_gstorage.upload_blob("ehms-myclub", "data/categories.csv", "categories.csv")
    copy_to_gstorage.upload_blob("ehms-myclub", "data/courses.csv", "courses.csv")
    copy_to_gstorage.upload_blob("ehms-myclub", "data/events.csv", "events.csv")
    copy_to_gstorage.upload_blob("ehms-myclub", "data/members.csv", "members.csv")
    copy_to_gstorage.upload_blob("ehms-myclub", "data/memberships.csv", "memberships.csv")
    copy_to_gstorage.upload_blob("ehms-myclub", "data/groups.csv", "groups.csv")
    copy_to_gstorage.upload_blob("ehms-myclub", "data/presences.csv", "presences.csv")

if __name__ == "__main__":
    run()
