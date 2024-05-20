import requests
import json
import headers


def member(member_id):

    base_url = "https://ehms.myclub.fi/api/"
    event_url = "members/" + member_id
    full_url = base_url + event_url
    response = requests.get(full_url, headers=headers.headers)
    content = json.loads(response.content)

    m = content.get("member")
    member = {
        "member_id": member_id,
        "first_name": m.get("first_name"),
        "last_name": m.get("last_name"),
        "email": m.get("email"),
    }

    return member


if __name__ == "__main__":
    print(json.dumps(member("387"), indent=2))
