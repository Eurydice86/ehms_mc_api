import requests
import json
import headers


def event(event_id):

    base_url = "https://ehms.myclub.fi/api/"

    event_url = "events/" + event_id
    full_url = base_url + event_url
    response = requests.get(full_url, headers=headers.headers)
    content = json.loads(response.content)

    event = content.get("event")
    name = event.get("name")
    starts_at = event.get("starts_at")
    ends_at = event.get("ends_at")
    group_id = event.get("group_id")
    venue_id = event.get("venue_id")
    course_id = event.get("course_id") if event.get("course_id") else "-"

    event_dict = {
        "event_id": event_id,
        "event_name": name,
        "starts_at": starts_at,
        "ends_at": ends_at,
        "group_id": group_id,
        "venue_id": venue_id,
        "course_id": course_id,
    }

    participants_list = []
    participations = content.get("participations")
    for p in participations:
        participation_dict = {
            "member_id": str(p.get("member_id")),
            "event_id": event_id,
            "confirmed": True if p.get("confirmed_at") else False,
        }
        participants_list.append(participation_dict)

    return (event_dict, participants_list)


if __name__ == "__main__":
    result = event("6582604")
    result = event("7031269")

    # print(json.dumps(result, indent=2))
