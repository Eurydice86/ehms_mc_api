import requests
import json
import datetime
import course
import os
from dotenv import load_dotenv
from logger import error, log
load_dotenv()

def courses_in_group(
    group_id,
    start=datetime.datetime.now() - datetime.timedelta(days=300),
    end=datetime.datetime.now(),
):
    """
    Fetch course IDs for a specific group within a date range.

    Args:
        group_id: The group ID to fetch courses for
        start: Start date (default: 300 days ago)
        end: End date (default: now)

    Returns:
        list: List of course ID strings

    Raises:
        ValueError: If MC_TOKEN is not set
        requests.exceptions.RequestException: If API request fails
    """
    myclub_token = os.getenv("MC_TOKEN")
    if not myclub_token:
        raise ValueError("MC_TOKEN environment variable is required but not set")

    headers = {"X-myClub-token": myclub_token}
    base_url = "https://ehms.myclub.fi/api/"
    full_url = f"{base_url}courses/"

    params = {"group_id": group_id, "start_date": start, "end_date": end}

    try:
        response = requests.get(full_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        content = response.json()

        courses_list = []
        for c in content:
            course_data = c.get("course")
            if course_data:
                courses_list.append(str(course_data.get("id")))

        return courses_list

    except requests.exceptions.HTTPError as e:
        error(f"HTTP error fetching courses for group {group_id}: {e}")
        raise
    except requests.exceptions.Timeout:
        error(f"Timeout fetching courses for group {group_id}")
        raise
    except requests.exceptions.RequestException as e:
        error(f"Request error fetching courses for group {group_id}: {e}")
        raise
    except json.JSONDecodeError as e:
        error(f"Invalid JSON response for courses in group {group_id}: {e}")
        raise


if __name__ == "__main__":
    lst = courses_in_group("28112")
    for i in lst:
        cs = course.course(i)
        log(json.dumps(cs, indent=2))
