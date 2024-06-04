import csv
import datetime
import os


def write_to_db(
    presences, events, courses, members, categories, groups, memberships, start, end
):
    directory = "data/" + str(end) + "/"
    os.mkdir(directory)
    write_events(events=events, directory=directory)
    write_presences(presences=presences, directory=directory)
    write_members(members=members, directory=directory)
    write_memberships(memberships=memberships, directory=directory)
    write_groups(groups=groups, directory=directory)
    write_categories(categories=categories, directory=directory)


def write_presences(presences, directory):
    filename = str(directory) + "presences.csv"
    with open(filename, "w", newline="") as presences_file:
        fieldnames = ["member_id", "event_id", "confirmed"]
        writer = csv.DictWriter(presences_file, fieldnames=fieldnames)

        writer.writeheader()
        for p in presences:
            writer.writerow(p)


def write_memberships(memberships, directory):
    filename = str(directory) + "memberships.csv"
    with open(filename, "w", newline="") as memberships_file:
        fieldnames = ["member_id", "group_id"]
        writer = csv.DictWriter(memberships_file, fieldnames=fieldnames)

        writer.writeheader()
        for m in memberships:
            writer.writerow(m)


def write_events(events, directory):
    filename = str(directory) + "events.csv"
    with open(filename, "w", newline="") as events_file:
        fieldnames = [
            "event_id",
            "event_name",
            "starts_at",
            "ends_at",
            "event_category_id",
            "group_id",
            "venue_id",
            "course_id",
        ]
        writer = csv.DictWriter(events_file, fieldnames=fieldnames)

        writer.writeheader()
        for ev in events:
            writer.writerow(ev)


def write_courses(courses, directory):
    filename = str(directory) + "courses.csv"
    with open(filename, "w", newline="") as courses_file:
        fieldnames = [
            "course_id",
            "course_name",
            "starts_at",
            "ends_at",
            "group_id",
        ]
        writer = csv.DictWriter(courses_file, fieldnames=fieldnames)

        writer.writeheader()
        for cs in courses:
            writer.writerow(cs)


def write_groups(groups, directory):
    filename = str(directory) + "groups.csv"
    with open(filename, "w", newline="") as groups_file:
        fieldnames = ["group_id", "group_name"]
        writer = csv.DictWriter(groups_file, fieldnames=fieldnames)

        writer.writeheader()
        for g in groups:
            writer.writerow(g)


def write_categories(categories, directory):
    filename = str(directory) + "categories.csv"
    with open(filename, "w", newline="") as categories_file:
        fieldnames = ["category_id", "category_name"]
        writer = csv.DictWriter(categories_file, fieldnames=fieldnames)

        writer.writeheader()
        for g in categories:
            writer.writerow(g)


def write_venues(venues, directory):
    filename = str(directory) + "venues.csv"
    with open(filename, "w", newline="") as venues_file:
        fieldnames = [
            "venue_id",
            "venue_name",
            "city",
            "street",
            "map_link",
        ]

        writer = csv.DictWriter(venues_file, fieldnames=fieldnames)
        writer.writeheader()
        for v in venues:
            writer.writerow(v)


def write_members(members, directory):
    filename = str(directory) + "members.csv"
    with open(filename, "w", newline="") as members_file:
        fieldnames = [
            "member_id",
            # "first_name",
            # "last_name",
            # "email",
            "active",
            "birthday",
            "country",
            "city",
            "gender",
        ]
        writer = csv.DictWriter(members_file, fieldnames=fieldnames)

        writer.writeheader()
        for m in members:
            writer.writerow(m)
