import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def member(member_id):
    """
    Fetch member details and memberships from MyClub API.

    Args:
        member_id: The member ID to fetch

    Returns:
        tuple: (member_dict, memberships_list) or (None, None) if member not found

    Raises:
        ValueError: If MC_TOKEN is not set or API returns invalid data
        requests.exceptions.RequestException: If API request fails
    """
    myclub_token = os.getenv("MC_TOKEN")
    if not myclub_token:
        raise ValueError("MC_TOKEN environment variable is required but not set")

    headers = {"X-myClub-token": myclub_token}
    base_url = "https://ehms.myclub.fi/api/"
    full_url = f"{base_url}members/{member_id}"

    try:
        response = requests.get(full_url, headers=headers, timeout=30)

        if response.status_code == 404:
            return (None, None)

        response.raise_for_status()
        content = response.json()

        member_data = content.get("member")
        if not member_data:
            raise ValueError(f"No member data returned for member_id {member_id}")

        # Extract date only from member_since (BigQuery DATE type)
        member_since_raw = member_data.get("created_at")
        member_since = None
        if member_since_raw:
            try:
                dt = datetime.fromisoformat(member_since_raw.replace('Z', '+00:00'))
                member_since = dt.date().isoformat()
            except (ValueError, AttributeError):
                pass

        member_dict = {
            "member_id": str(member_id),
            "active": bool(member_data.get("active")) if member_data.get("active") is not None else None,
            "birthday": member_data.get("birthday"),
            "country": member_data.get("country"),
            "city": member_data.get("city"),
            "gender": member_data.get("gender"),
            "member_since": member_since,
        }

        memberships = []
        for q in member_data.get("memberships", []):
            membership = {
                "member_id": str(member_id),
                "group_id": str(q.get("group_id")) if q.get("group_id") is not None else None
            }
            memberships.append(membership)

        return member_dict, memberships

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching member {member_id}: {e}")
        raise
    except requests.exceptions.Timeout:
        print(f"Timeout fetching member {member_id}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching member {member_id}: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response for member {member_id}: {e}")
        raise


if __name__ == "__main__":
    members_list = [
        "347",
    ]
    for mem in members_list:
        m, memberships = member(mem)
        print(json.dumps(m, indent=2))
