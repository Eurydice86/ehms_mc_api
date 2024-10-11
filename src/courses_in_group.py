import requests
import json
import datetime
import course
import os
from dotenv import load_dotenv
load_dotenv()

def courses_in_group(
    group_id,
    start=datetime.datetime.now() - datetime.timedelta(days=300),
    end=datetime.datetime.now(),
):

    myclub_token = os.getenv("MC_TOKEN")
    headers = {"X-myClub-token": myclub_token}
    
    base_url = "https://ehms.myclub.fi/api/"
    course_url = "courses/"
    full_url = base_url + course_url

    params = {"group_id": group_id, "start_date": start, "end_date": end}

    response = requests.get(full_url, headers=headers, params=params)
    content = json.loads(response.content)

    courses_list = []
    for c in content:
        c = c.get("course")
        courses_list.append(str(c.get("id")))

    return courses_list


if __name__ == "__main__":
    lst = courses_in_group("28112")
    for i in lst:
        cs = course.course(i)
        print(json.dumps(cs, indent=2))
