import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

def course(course_id):

    myclub_token = os.getenv("MC_TOKEN")
    headers = {"X-myClub-token": myclub_token}

    base_url = "https://ehms.myclub.fi/api/"

    course_url = "courses/" + course_id
    full_url = base_url + course_url
    response = requests.get(full_url, headers=headers)
    content = json.loads(response.content)

    course = content.get("course")

    course_name = course.get("name")
    starts_at = course.get("starts_at")
    ends_at = course.get("ends_at")
    group_id = course.get("group_id")

    course_dict = {
        "course_id": course_id,
        "course_name": course_name,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "group_id": group_id,
    }

    return course_dict


if __name__ == "__main__":
    cs = course("7031269")
    print(json.dumps(cs, indent=2))
