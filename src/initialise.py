import datetime

import get_all_presences
import db_sql
import categories
import groups
import params

import json


def run():

    # end = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    # start = end - datetime.timedelta(days=7)
    # start = "2024-01-20"
    # end = "2024-05-30"
    start = params.start_date
    start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    # end = datetime.datetime.strptime(end, "%Y-%m-%d").date()

    interval = 30
    # either 30 days after start or yesterday (today might still have ongoing events)

    end = min(
        start + datetime.timedelta(days=interval),
        (datetime.datetime.now() - datetime.timedelta(days=1)).date(),
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
    db_sql.add_rows("members", members)
    db_sql.add_rows("memberships", memberships)
    db_sql.add_rows("groups", _groups)
    db_sql.add_rows("presences", presences)

    with open("params.py", "w") as file:
        file.write('start_date = "' + str(end + datetime.timedelta(days=1)) + '"')


if __name__ == "__main__":
    run()
