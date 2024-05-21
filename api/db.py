import csv


def write_presences(presences):
    with open("data/presences.csv", "w", newline="") as presences_file:
        fieldnames = ["member_id", "event_id"]
        writer = csv.DictWriter(presences_file, fieldnames=fieldnames)

        writer.writeheader()
        for p in presences:
            writer.writerow(p)


def write_events(events):
    with open("data/events.csv", "w", newline="") as events_file:
        fieldnames = [
            "event_id",
            "event_name",
            "starts_at",
            "ends_at",
            "group_id",
            "venue_id",
            "course_id",
        ]
        writer = csv.DictWriter(events_file, fieldnames=fieldnames)

        writer.writeheader()
        for ev in events:
            writer.writerow(ev)


def write_groups(groups):
    with open("data/groups.csv", "w", newline="") as groups_file:
        fieldnames = ["group_id", "group_name"]
        writer = csv.DictWriter(groups_file, fieldnames=fieldnames)

        writer.writeheader()
        for g in groups:
            writer.writerow(g)


def write_members(members):
    with open("data/members.csv", "w", newline="") as members_file:
        fieldnames = [
            "member_id",
            "birthday",
            "country",
            "city",
            "gender",
        ]
        writer = csv.DictWriter(members_file, fieldnames=fieldnames)

        writer.writeheader()
        for m in members:
            writer.writerow(m)
