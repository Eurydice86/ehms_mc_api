import requests
import json
import headers


def main():

    base_url = "https://ehms.myclub.fi/api/"
    event_url = "events/6582444"  # group 48332

    full_url = base_url + event_url

    response = requests.get(full_url, headers=headers.headers)

    content = json.loads(response.content)

    v = content.get("participations")
    for vl in v:
        print(vl.get("member_id"))


if __name__ == "__main__":
    main()
