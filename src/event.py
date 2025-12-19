import requests
import json
import os

from dotenv import load_dotenv

load_dotenv()

def event(event_id):
    """
    Fetch event details and participations from MyClub API.

    Args:
        event_id: The event ID to fetch

    Returns:
        tuple: (event_dict, participants_list)

    Raises:
        ValueError: If MC_TOKEN is not set or API returns invalid data
        requests.exceptions.RequestException: If API request fails
    """
    myclub_token = os.getenv("MC_TOKEN")
    if not myclub_token:
        raise ValueError("MC_TOKEN environment variable is required but not set")

    headers = {"X-myClub-token": myclub_token}
    base_url = "https://ehms.myclub.fi/api/"
    full_url = f"{base_url}events/{event_id}"

    try:
        response = requests.get(full_url, headers=headers, timeout=30)
        response.raise_for_status()
        content = response.json()

        event_data = content.get("event")
        if not event_data:
            raise ValueError(f"No event data returned for event_id {event_id}")

        event_dict = {
            "event_id": str(event_id),
            "event_name": event_data.get("name"),
            "starts_at": event_data.get("starts_at"),
            "ends_at": event_data.get("ends_at"),
            "event_category_id": str(event_data.get("event_category_id")) if event_data.get("event_category_id") is not None else None,
            "group_id": str(event_data.get("group_id")) if event_data.get("group_id") is not None else None,
            "venue_id": str(event_data.get("venue_id")) if event_data.get("venue_id") is not None else None,
            "course_id": str(event_data.get("course_id")) if event_data.get("course_id") is not None else None,
        }

        participants_list = []
        participations = content.get("participations", [])
        for p in participations:
            participation_dict = {
                "member_id": str(p.get("member_id")),
                "event_id": str(event_id),
                "confirmed": bool(p.get("confirmed_at")),
            }
            participants_list.append(participation_dict)

        return (event_dict, participants_list)

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching event {event_id}: {e}")
        raise
    except requests.exceptions.Timeout:
        print(f"Timeout fetching event {event_id}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching event {event_id}: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response for event {event_id}: {e}")
        raise


if __name__ == "__main__":
    result = event("8177017")

    print(json.dumps(result, indent=2))
