import datetime
import groups
import events_in_group
import event
import member
import db
import venues


def get_all_presences_in_date_range(start, end):
    print(f"From: {start} to {end}")
    groups_list = groups.get_group_ids()
    venues.venues()
    group_ids_list = [g.get("group_id") for g in groups_list]

    events_list = []
    members_list = []
    presences_list = []
    event_dict_list = []
    members_dict_list = []
    membership_dict_list = []

    for group in group_ids_list:
        events = events_in_group.events_in_group(group, start=start, end=end)
        events_list.extend(events)

    for ev in events_list:
        event_dict, presences = event.event(ev)
        event_dict_list.append(event_dict)
        presences_list.extend(presences)

    for p in presences_list:
        m = p.get("member_id")
        members_list.append(m)

    members_list = list(set(members_list))

    for m in members_list:
        member_dict, membership_dict = member.member(m)
        members_dict_list.append(member_dict)
        membership_dict_list.extend(membership_dict)

    return presences_list, event_dict_list, members_dict_list, membership_dict_list


if __name__ == "__main__":
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=1)
    presences, events, members, memberships = get_all_presences_in_date_range(
        start, end
    )

    db.write_events(events=events)
    db.write_presences(presences=presences)
    db.write_members(members=members)
    db.write_memberships(memberships=memberships)
