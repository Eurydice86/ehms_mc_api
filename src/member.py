import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


def member(member_id):
    myclub_token = os.getenv("MC_TOKEN")
    headers = {"X-myClub-token": myclub_token}
    base_url = "https://ehms.myclub.fi/api/"
    event_url = "members/" + member_id
    full_url = base_url + event_url
    response = requests.get(full_url, headers=headers)
    if response.status_code == 404:
        return (None, None)

    content = json.loads(response.content)

    m = content.get("member")

    member = {
        "member_id": member_id,
        # "first_name": m.get("first_name"),
        # "last_name": m.get("last_name"),
        # "email": m.get("email"),
        "active": m.get("active"),
        "birthday": m.get("birthday"),
        "country": m.get("country"),
        "city": m.get("city"),
        "gender": m.get("gender"),
        "member_since": m.get("created_at"),
    }

    memberships = []
    for q in m.get("memberships"):
        membership = {"member_id": member_id, "group_id": q.get("group_id")}
        memberships.append(membership)

    return member, memberships


if __name__ == "__main__":
    members_list = [
        "347",
    ]
    for mem in members_list:
        m, memberships = member(mem)
        print(json.dumps(m, indent=2))
