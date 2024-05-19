import datetime
import groups
import events_in_group
import event
import csv


def get_all_presences(start, end):
    print(f"From: {start} to {end}")
    groups_list = groups.get_group_ids()

    events_list = []
    presences_list = []

    for group in groups_list:
        events = events_in_group.events_in_group(group, start=start, end=end)
        events_list.extend(events)

    for ev in events_list:
        presences = event.event(ev)
        presences_list.extend(presences)

    return presences_list


if __name__ == "__main__":
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=7)
    presences = get_all_presences(start, end)

    with open("data/presences.csv", "w", newline="") as presences_file:
        fieldnames = ["member_id", "event_id"]
        writer = csv.DictWriter(presences_file, fieldnames=fieldnames)

        writer.writeheader()
        for p in presences:
            writer.writerow(p)
