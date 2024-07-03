import sqlite3

db_name = "ehms.db"

# schema
categories = """
categories(
category_id TEXT PRIMARY KEY,
category_name TEXT
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
    print("connection opened")
    cursor = conn.cursor()

    # Create tables
    cursor.execute(create_table(categories))
    cursor.execute(create_table(events))
    cursor.execute(create_table(groups))
    cursor.execute(create_table(members))
    cursor.execute(create_table(memberships))
    cursor.execute(create_table(presences))

    conn.commit()
    conn.close()
    print("connection closed")


def create_table(table: str) -> str:
    command: str = f"CREATE TABLE IF NOT EXISTS {table};"
    return command


def add_rows(table: str, entries) -> None:
    if not entries:
        print(f"no entries for {table}")
        return
    conn = sqlite3.connect(database=db_name)
    cursor = conn.cursor()
    print(f"connection opened for {table}")

    values_list = ""
    for e in entries:
        values_list += "('" + "', '".join(str(val) for val in e.values()) + "'),\n"
    insert = f"""INSERT OR IGNORE INTO {table} VALUES {values_list[:-2]};"""

    cursor.execute(insert)

    conn.commit()
    conn.close()
    print("connection closed")
