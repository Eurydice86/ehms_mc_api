import requests
import json
import datetime


def main():

    base_url = "https://ehms.myclub.fi/api/"
    headers = {"X-myClub-token": "bb8049d99d974aa7793db6be20442d6d"}

    now = datetime.datetime.now()
    last_week = now - datetime.timedelta(days=7)

    print(now)
    print(last_week)

    full_url = base_url + "events"

    params = {"group_id": "28112",
              "start_date": last_week,
              "end_date": now}

    response = requests.get(full_url, headers=headers, params=params)

    content = json.loads(response.content)
    print(json.dumps(content, indent=2))


if __name__ == "__main__":
    main()
