import datetime

import get_all_presences
import db
import categories
import groups

if __name__ == "__main__":

    # end = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
    # start = end - datetime.timedelta(days=7)
    start = "2023-08-20"
    end = "2023-09-30"
    start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
    # end = min(start + datetime.timedelta(days=30), datetime.datetime.now().date()) # either 30 days after start or today

    presences, events, courses, members, memberships = (
        get_all_presences.get_all_presences_in_date_range(start, end)
    )

    categories = categories.categories()
    groups = groups.get_group_ids()

    db.write_to_db(
        presences, events, courses, members, categories, groups, memberships, start, end
    )
