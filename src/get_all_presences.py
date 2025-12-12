import groups
import events_in_group
import event
import courses_in_group
import course
import member
import venues
import datetime


def get_all_presences_in_date_range(start, end):
    print(f"From: {start} to {end}")
    groups_list = groups.get_group_ids()
    venues.venues(start)
    group_ids_list = [g.get("group_id") for g in groups_list]

    events_list = []
    courses_list = []
    members_list = []
    presences_list = []
    event_dict_list = []
    course_dict_list = []
    members_dict_list = []
    membership_dict_list = []

    print(f"Fetching events and courses for {len(group_ids_list)} groups...")
    for idx, group in enumerate(group_ids_list, 1):
        print(f"  Processing group {idx}/{len(group_ids_list)}", end='\r')
        events = events_in_group.events_in_group(group, start=start, end=end)
        events_list.extend(events)

        courses = courses_in_group.courses_in_group(group, start=start, end=end)
        courses_list.extend(courses)
    print(f"  Completed: {len(events_list)} events, {len(courses_list)} courses found")

    print(f"Processing {len(events_list)} events...")
    for idx, ev in enumerate(events_list, 1):
        if idx % 10 == 0 or idx == len(events_list):
            print(f"  Processing event {idx}/{len(events_list)}", end='\r')
        event_dict, presences = event.event(ev)
        event_dict_list.append(event_dict)
        presences_list.extend(presences)
    print(f"  Completed: {len(presences_list)} presences found")

    print(f"Processing {len(courses_list)} courses...")
    for idx, cs in enumerate(courses_list, 1):
        if idx % 10 == 0 or idx == len(courses_list):
            print(f"  Processing course {idx}/{len(courses_list)}", end='\r')
        course_dict = course.course(cs)
        course_dict_list.append(course_dict)
        presences_list.extend(presences)
    if courses_list:
        print(f"  Completed")

    print("Collecting unique members...")
    for p in presences_list:
        m = p.get("member_id")
        members_list.append(m)

    members_list = list(set(members_list))
    print(f"Found {len(members_list)} unique members")

    print(f"Fetching member details...")
    for idx, m in enumerate(members_list, 1):
        if idx % 10 == 0 or idx == len(members_list):
            print(f"  Processing member {idx}/{len(members_list)}", end='\r')
        member_dict, membership_dict = member.member(m)
        if member_dict and membership_dict:
            members_dict_list.append(member_dict)
            membership_dict_list.extend(membership_dict)
    print(f"  Completed: {len(members_dict_list)} members processed")

    return (
        presences_list,
        event_dict_list,
        course_dict_list,
        members_dict_list,
        membership_dict_list,
    )


if __name__ == "__main__":
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=1)
    get_all_presences_in_date_range()
