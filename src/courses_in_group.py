import requests
import json
import headers
import datetime
import course


def courses_in_group(
    group_id,
    start=datetime.datetime.now() - datetime.timedelta(days=300),
    end=datetime.datetime.now(),
):

    base_url = "https://ehms.myclub.fi/api/"
    course_url = "courses/"
    full_url = base_url + course_url

    params = {"group_id": group_id, "start_date": start, "end_date": end}

    response = requests.get(full_url, headers=headers.headers, params=params)
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
