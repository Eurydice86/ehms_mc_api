import requests
import json
import os
from dotenv import load_dotenv
from logger import error, log
load_dotenv()

def course(course_id):
    """
    Fetch course details from MyClub API.

    Args:
        course_id: The course ID to fetch

    Returns:
        dict: Course details

    Raises:
        ValueError: If MC_TOKEN is not set or API returns invalid data
        requests.exceptions.RequestException: If API request fails
    """
    myclub_token = os.getenv("MC_TOKEN")
    if not myclub_token:
        raise ValueError("MC_TOKEN environment variable is required but not set")

    headers = {"X-myClub-token": myclub_token}
    base_url = "https://ehms.myclub.fi/api/"
    full_url = f"{base_url}courses/{course_id}"

    try:
        response = requests.get(full_url, headers=headers, timeout=30)
        response.raise_for_status()
        content = response.json()

        course_data = content.get("course")
        if not course_data:
            raise ValueError(f"No course data returned for course_id {course_id}")

        course_dict = {
            "course_id": str(course_id),
            "course_name": course_data.get("name"),
            "starts_at": course_data.get("starts_at"),
            "ends_at": course_data.get("ends_at"),
            "group_id": str(course_data.get("group_id")) if course_data.get("group_id") is not None else None,
        }

        return course_dict

    except requests.exceptions.HTTPError as e:
        error(f"HTTP error fetching course {course_id}: {e}")
        raise
    except requests.exceptions.Timeout:
        error(f"Timeout fetching course {course_id}")
        raise
    except requests.exceptions.RequestException as e:
        error(f"Request error fetching course {course_id}: {e}")
        raise
    except json.JSONDecodeError as e:
        error(f"Invalid JSON response for course {course_id}: {e}")
        raise


if __name__ == "__main__":
    cs = course("7031269")
    log(json.dumps(cs, indent=2))
