import requests
import json
import os
from dotenv import load_dotenv
from logger import error

load_dotenv()

def categories():
    """
    Fetch all event categories from MyClub API.

    Returns:
        list: List of category dictionaries with category_id and category_name

    Raises:
        ValueError: If MC_TOKEN is not set
        requests.exceptions.RequestException: If API request fails
    """
    myclub_token = os.getenv("MC_TOKEN")
    if not myclub_token:
        raise ValueError("MC_TOKEN environment variable is required but not set")

    headers = {"X-myClub-token": myclub_token}
    base_url = "https://ehms.myclub.fi/api/"
    full_url = f"{base_url}event_categories"

    try:
        response = requests.get(full_url, headers=headers, timeout=30)
        response.raise_for_status()
        content = response.json()

        categories_list = []
        for cat in content:
            cat_data = cat.get("event_category")
            if cat_data:
                category_id = str(cat_data.get("id"))
                category_name = cat_data.get("name")
                categories_list.append(
                    {"category_id": category_id, "category_name": category_name}
                )

        return categories_list

    except requests.exceptions.HTTPError as e:
        error(f"HTTP error fetching categories: {e}")
        raise
    except requests.exceptions.Timeout:
        error(f"Timeout fetching categories")
        raise
    except requests.exceptions.RequestException as e:
        error(f"Request error fetching categories: {e}")
        raise
    except json.JSONDecodeError as e:
        error(f"Invalid JSON response for categories: {e}")
        raise


if __name__ == "__main__":
    categories()
