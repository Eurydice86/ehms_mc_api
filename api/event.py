import requests
import json
import headers


def event(event_id):

    base_url = "https://ehms.myclub.fi/api/"

    event_url = "events/" + event_id
    full_url = base_url + event_url
    response = requests.get(full_url, headers=headers.headers)
    content = json.loads(response.content)

    participants_list = []
    v = content.get("participations")
    for vl in v:
        participation_dict = {
            "member_id": str(vl.get("member_id")),
            "event_id": event_id,
        }
        # print(vl.get("member_id"), vl.get("self_registration"))
        participants_list.append(participation_dict)

    return participants_list


if __name__ == "__main__":
    result = event("6582604")
    print(json.dumps(result, indent=2))
