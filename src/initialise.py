import datetime

import get_all_presences
import db
import db_sql
import categories
import groups
import params

if __name__ == "__main__":

    # end = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    # start = end - datetime.timedelta(days=7)
    # start = "2024-01-20"
    # end = "2024-05-30"
    start = params.start_date
    start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    # end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
    end = min(
        start + datetime.timedelta(days=30),
        (datetime.datetime.now() - datetime.timedelta(days=1)).date(),
    )  # either 30 days after start or yesterday (today might still have ongoing events)

    presences, events, courses, members, memberships = (
        get_all_presences.get_all_presences_in_date_range(start, end)
    )

    categories = categories.categories()
    groups = groups.get_group_ids()

    """"""
    db_sql.initialise_db()
    db_sql.add_rows("categories", categories)
    db_sql.add_rows("courses", courses)
    db_sql.add_rows("members", members)
    db_sql.add_rows("events", events)
    db_sql.add_rows("memberships", memberships)
    db_sql.add_rows("groups", groups)
    db_sql.add_rows("presences", presences)

    """"""
    db.write_to_db(
        presences, events, courses, members, categories, groups, memberships, start, end
    )

    with open("params.py", "w") as file:
        file.write('start_date = "' + str(end + datetime.timedelta(days=1)) + '"')
