import requests
import json
import os

from dotenv import load_dotenv

load_dotenv()

def get_group_ids():
    """
    Fetch all groups from MyClub API.

    Returns:
        list: List of group dictionaries with group_id and group_name

    Raises:
        ValueError: If MC_TOKEN is not set
        requests.exceptions.RequestException: If API request fails
    """
    myclub_token = os.getenv("MC_TOKEN")
    if not myclub_token:
        raise ValueError("MC_TOKEN environment variable is required but not set")

    base_url = "https://ehms.myclub.fi/api/"
    headers = {"X-myClub-token": myclub_token}
    full_url = f"{base_url}groups"

    try:
        response = requests.get(full_url, headers=headers, timeout=30)
        response.raise_for_status()
        content = response.json()

        groups_list = []
        for c in content:
            group_data = c.get("group")
            if group_data:
                group_id = str(group_data.get("id"))
                group_name = group_data.get("name")
                groups_list.append({"group_id": group_id, "group_name": group_name})

        return groups_list

    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching groups: {e}")
        raise
    except requests.exceptions.Timeout:
        print(f"Timeout fetching groups")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching groups: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response for groups: {e}")
        raise


if __name__ == "__main__":
    get_group_ids()
