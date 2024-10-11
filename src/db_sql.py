import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

db_name = os.getenv("DB")

# schema
categories = """
categories(
category_id TEXT PRIMARY KEY,
category_name TEXT
)
"""

courses = """
courses(
course_id TEXT PRIMARY KEY,
course_name TEXT,
starts_at TEXT,
ends_at TEXT,
group_id TEXT
)
"""

events = """
events(
event_id TEXT PRIMARY KEY,
event_name TEXT,
starts_at TEXT,
ends_at TEXT,
event_category_id TEXT,
group_id TEXT,
venue_id TEXT,
course_id TEXT
)
"""

groups = """
groups(
group_id TEXT PRIMARY KEY,
group_name TEXT
)
"""

members = """
members(
member_id TEXT PRIMARY KEY,
active TEXT,
birthday TEXT,
country TEXT,
city TEXT,
gender TEXT,
member_since TEXT)
"""

memberships = """
memberships(
member_id TEXT,
group_id TEXT
)
"""

presences = """
presences(
member_id TEXT,
event_id TEXT,
confirmed TEXT)
"""


def initialise_db() -> None:
    # Open connection
    conn = sqlite3.connect(database=db_name)
    cursor = conn.cursor()

    # Create tables
    cursor.execute(create_table(categories))
    cursor.execute(create_table(courses))
    cursor.execute(create_table(events))
    cursor.execute(create_table(groups))
    cursor.execute(create_table(members))
    cursor.execute(create_table(memberships))
    cursor.execute(create_table(presences))

    conn.commit()
    conn.close()


def create_table(table: str) -> str:
    command: str = f"CREATE TABLE IF NOT EXISTS {table};"
    return command


def add_rows(table: str, entries) -> None:
    if not entries:
        print(f"No entries for {table}")
        return
    conn = sqlite3.connect(database=db_name)
    cursor = conn.cursor()

    values_list = ""
    for e in entries:
        values_list += "('" + "', '".join(str(val) for val in e.values()) + "'),\n"
    insert = f"""INSERT OR IGNORE INTO {table} VALUES {values_list[:-2]};"""

    cursor.execute(insert)

    conn.commit()
    conn.close()


def most_recent_date() -> str:
    conn = sqlite3.connect(database=db_name)
    cursor = conn.cursor()

    command = "SELECT MAX(starts_at) FROM events;"
    date = cursor.execute(command).fetchone()[0]

    conn.commit()
    conn.close()

    return date
