import requests
import json
import headers
import db


def member(member_id):

    base_url = "https://ehms.myclub.fi/api/"
    event_url = "members/" + member_id
    full_url = base_url + event_url
    response = requests.get(full_url, headers=headers.headers)
    content = json.loads(response.content)

    m = content.get("member")
    member = {
        "member_id": member_id,
        # "first_name": m.get("first_name"),
        # "last_name": m.get("last_name"),
        # "email": m.get("email"),
        "birthday": m.get("birthday"),
        "country": m.get("country"),
        "city": m.get("city"),
        "gender": m.get("gender"),
    }

    memberships = []
    for q in m.get("memberships"):
        membership = {
            "member_id": member_id,
            "group_id": q.get("group_id")
        }
        memberships.append(membership)

    return member, memberships


if __name__ == "__main__":
    print(json.dumps(member("347"), indent=2))
