import requests
import json
import os
from dotenv import load_dotenv
from logger import error

load_dotenv()

def venues():
    """
    Fetch all venues from MyClub API.

    Returns:
        list: List of venue dictionaries

    Raises:
        ValueError: If MC_TOKEN is not set
        requests.exceptions.RequestException: If API request fails
    """
    myclub_token = os.getenv("MC_TOKEN")
    if not myclub_token:
        raise ValueError("MC_TOKEN environment variable is required but not set")

    headers = {"X-myClub-token": myclub_token}
    base_url = "https://ehms.myclub.fi/api/"
    full_url = f"{base_url}venues"

    try:
        response = requests.get(full_url, headers=headers, timeout=30)
        response.raise_for_status()
        content = response.json()

        venues_list = []
        for v in content:
            venue_data = v.get("venue")
            if venue_data:
                venue_id = venue_data.get("id")
                venue_name = venue_data.get("name")
                city = venue_data.get("city")
                street = venue_data.get("street")
                map_link = venue_data.get("map_link")
                venues_list.append(
                    {
                        "venue_id": venue_id,
                        "venue_name": venue_name,
                        "city": city,
                        "street": street,
                        "map_link": map_link,
                    }
                )

        return venues_list

    except requests.exceptions.HTTPError as e:
        error(f"HTTP error fetching venues: {e}")
        raise
    except requests.exceptions.Timeout:
        error(f"Timeout fetching venues")
        raise
    except requests.exceptions.RequestException as e:
        error(f"Request error fetching venues: {e}")
        raise
    except json.JSONDecodeError as e:
        error(f"Invalid JSON response for venues: {e}")
        raise


if __name__ == "__main__":
    venues()
