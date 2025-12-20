import groups
import events_in_group
import event
import courses_in_group
import course
import member
import venues
import datetime


def progress_bar(current, total, width=30):
    """Generate a progress bar string."""
    percentage = current / total if total > 0 else 0
    filled = int(width * percentage)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {current}/{total}"


def get_all_presences_in_date_range(start, end):
    """
    Fetch all presences, events, courses, members, and memberships for a date range.

    This function orchestrates the entire data collection process:
    1. Fetches all groups and venues
    2. Gets events and courses for each group in the date range
    3. Collects event details and participant presences
    4. Fetches unique member details and their memberships

    Args:
        start (datetime.date): Start date for event range
        end (datetime.date): End date for event range

    Returns:
        tuple: (presences_list, event_dict_list, course_dict_list,
                members_dict_list, membership_dict_list)
    """
    print(f"From: {start} to {end}")
    groups_list = groups.get_group_ids()
    venues.venues()
    group_ids_list = [g.get("group_id") for g in groups_list]

    events_list = []
    courses_list = []
    members_list = []
    presences_list = []
    event_dict_list = []
    course_dict_list = []
    members_dict_list = []
    membership_dict_list = []

    for idx, group in enumerate(group_ids_list, 1):
        bar = progress_bar(idx, len(group_ids_list))
        print(f"Fetching events and courses for {len(group_ids_list)} groups... {bar}", end='\r')
        events = events_in_group.events_in_group(group, start=start, end=end)
        events_list.extend(events)

        courses = courses_in_group.courses_in_group(group, start=start, end=end)
        courses_list.extend(courses)
    bar = progress_bar(len(group_ids_list), len(group_ids_list))
    print(f"Fetching events and courses for {len(group_ids_list)} groups... {bar} completed" + " " * 10)

    for idx, ev in enumerate(events_list, 1):
        bar = progress_bar(idx, len(events_list))
        print(f"Processing {len(events_list)} events... {bar}", end='\r')
        event_dict, presences = event.event(ev)
        event_dict_list.append(event_dict)
        presences_list.extend(presences)
    bar = progress_bar(len(events_list), len(events_list))
    print(f"Processing {len(events_list)} events... {bar} completed" + " " * 10)

    for idx, cs in enumerate(courses_list, 1):
        bar = progress_bar(idx, len(courses_list))
        print(f"Processing {len(courses_list)} courses... {bar}", end='\r')
        course_dict = course.course(cs)
        course_dict_list.append(course_dict)
    if courses_list:
        bar = progress_bar(len(courses_list), len(courses_list))
        print(f"Processing {len(courses_list)} courses... {bar} completed" + " " * 10)

    members_set = set()
    for p in presences_list:
        members_set.add(p.get("member_id"))

    members_list = list(members_set)

    for idx, m in enumerate(members_list, 1):
        bar = progress_bar(idx, len(members_list))
        print(f"Processing {len(members_list)} members... {bar}", end='\r')
        member_dict, membership_dict = member.member(m)
        if member_dict and membership_dict:
            members_dict_list.append(member_dict)
            membership_dict_list.extend(membership_dict)
    bar = progress_bar(len(members_list), len(members_list))
    print(f"Processing {len(members_list)} members... {bar} completed" + " " * 10)

    return (
        presences_list,
        event_dict_list,
        course_dict_list,
        members_dict_list,
        membership_dict_list,
    )


if __name__ == "__main__":
    end = datetime.datetime.now().date()
    start = end - datetime.timedelta(days=1)
    get_all_presences_in_date_range(start, end)
