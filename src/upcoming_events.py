import groups
import events_in_group
import event

import datetime
import requests
import json
import os

from dotenv import load_dotenv
from logger import error, log

load_dotenv()


def upcoming_events_in_non_EHMS_venue():
    """
    Fetch upcoming events in non-EHMS venue for the next ~4 months.

    Returns:
        list: List of [event_id, event_name, starts_at] for each event

    Raises:
        ValueError: If MC_TOKEN or required env vars are not set
        requests.exceptions.RequestException: If API request fails
    """
    # Get configuration from environment variables
    special_group_id = os.getenv("SPECIAL_GROUP_ID", "28105")
    non_ehms_venue_id = os.getenv("NON_EHMS_VENUE_ID", "126179")

    start = datetime.datetime.now().date()
    # Calculate end date: first day of month, ~4 months ahead
    end = (start.replace(day=1) + datetime.timedelta(days=128)).replace(day=1)

    log(f"Fetching events from {start} to {end}")

    myclub_token = os.getenv("MC_TOKEN")
    if not myclub_token:
        raise ValueError("MC_TOKEN environment variable is required but not set")

    headers = {"X-myClub-token": myclub_token}
    base_url = "https://ehms.myclub.fi/api/"
    full_url = f"{base_url}events/"

    params = {
        "group_id": special_group_id,
        "venue_id": non_ehms_venue_id,
        "start_date": start,
        "end_date": end
    }

    try:
        response = requests.get(full_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        content = response.json()

        events_list = []
        for c in content:
            event_data = c.get("event")
            if event_data:
                events_list.append([
                    str(event_data.get("id")),
                    event_data.get("name"),
                    event_data.get("starts_at")
                ])

        return events_list

    except requests.exceptions.HTTPError as e:
        error(f"HTTP error fetching upcoming events: {e}")
        raise
    except requests.exceptions.Timeout:
        error(f"Timeout fetching upcoming events")
        raise
    except requests.exceptions.RequestException as e:
        error(f"Request error fetching upcoming events: {e}")
        raise
    except json.JSONDecodeError as e:
        error(f"Invalid JSON response for upcoming events: {e}")
        raise


if __name__ == "__main__":
    lst = upcoming_events_in_non_EHMS_venue()
    log(lst)
