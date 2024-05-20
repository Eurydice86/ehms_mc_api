import requests
import json
import headers


def course(course_id):

    base_url = "https://ehms.myclub.fi/api/"

    course_url = "courses/" + course_id
    full_url = base_url + course_url
    response = requests.get(full_url, headers=headers.headers)
    content = json.loads(response.content)

    course = content.get("course")

    name = course.get("name")
    print(course.get("starts_at"))
    print(course.get("ends_at"))
    print(course.get("group_id"))

    participants_list = []
    participations = content.get("participations")
    for p in participations:
        participation_dict = {
            "member_id": str(p.get("member_id")),
            "course_id": course_id,
        }
        participants_list.append(participation_dict)

    return participants_list


if __name__ == "__main__":
    result = course("7031269")

    # print(json.dumps(result, indent=2))
