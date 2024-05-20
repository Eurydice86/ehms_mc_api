import datetime
import groups
import events_in_group
import event
import db


def get_all_presences_in_date_range(start, end):
    print(f"From: {start} to {end}")
    groups_list = groups.get_group_ids()
    group_ids_list = [g.get("group_id") for g in groups_list]

    events_list = []
    presences_list = []
    event_dict_list = []

    for group in group_ids_list:
        events = events_in_group.events_in_group(group, start=start, end=end)
        events_list.extend(events)

    for ev in events_list:
        event_dict, presences = event.event(ev)
        event_dict_list.append(event_dict)
        presences_list.extend(presences)

    return presences_list, event_dict_list


if __name__ == "__main__":
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=30)
    presences, events = get_all_presences_in_date_range(start, end)

    db.write_events(events=events)
    db.write_presences(presences=presences)
