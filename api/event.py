import requests
import json


def main():

    base_url = "https://ehms.myclub.fi/api/"
    headers = {"X-myClub-token": "bb8049d99d974aa7793db6be20442d6d"}
    event_url = "events/6582444"  # group 48332

    full_url = base_url + event_url

    response = requests.get(full_url, headers=headers)

    content = json.loads(response.content)

    v = content.get("participations")
    for vl in v:
        print(vl.get("member_id"))


if __name__ == "__main__":
    main()
