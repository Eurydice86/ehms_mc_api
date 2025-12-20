import requests
import json
import datetime
import event
import os

from dotenv import load_dotenv
from logger import error, log
load_dotenv()

def events_in_group(
    group_id,
    start=datetime.datetime.now() - datetime.timedelta(days=7),
    end=datetime.datetime.now(),
):
    """
    Fetch event IDs for a specific group within a date range.

    Args:
        group_id: The group ID to fetch events for
        start: Start date (default: 7 days ago)
        end: End date (default: now)

    Returns:
        list: List of event ID strings

    Raises:
        ValueError: If MC_TOKEN is not set
        requests.exceptions.RequestException: If API request fails
    """
    myclub_token = os.getenv("MC_TOKEN")
    if not myclub_token:
        raise ValueError("MC_TOKEN environment variable is required but not set")

    headers = {"X-myClub-token": myclub_token}
    base_url = "https://ehms.myclub.fi/api/"
    full_url = f"{base_url}events/"

    params = {"group_id": group_id, "start_date": start, "end_date": end}

    try:
        response = requests.get(full_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        content = response.json()

        events_list = []
        for c in content:
            event_data = c.get("event")
            if event_data:
                events_list.append(str(event_data.get("id")))

        return events_list

    except requests.exceptions.HTTPError as e:
        error(f"HTTP error fetching events for group {group_id}: {e}")
        raise
    except requests.exceptions.Timeout:
        error(f"Timeout fetching events for group {group_id}")
        raise
    except requests.exceptions.RequestException as e:
        error(f"Request error fetching events for group {group_id}: {e}")
        raise
    except json.JSONDecodeError as e:
        error(f"Invalid JSON response for events in group {group_id}: {e}")
        raise


if __name__ == "__main__":
    lst = events_in_group("28112")
    for i in lst:
        ev, q = event.event(i)
        log(json.dumps(ev, indent=2))
