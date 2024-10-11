import requests
import json
import datetime
import event

import os

from dotenv import load_dotenv
load_dotenv()

def events_in_group(
    group_id,
    start=datetime.datetime.now() - datetime.timedelta(days=7),
    end=datetime.datetime.now(),
):
    myclub_token = os.getenv("MC_TOKEN")
    headers = {"X-myClub-token": myclub_token}

    base_url = "https://ehms.myclub.fi/api/"
    event_url = "events/"
    full_url = base_url + event_url

    params = {"group_id": group_id, "start_date": start, "end_date": end}

    response = requests.get(full_url, headers=headers, params=params)
    content = json.loads(response.content)

    events_list = []
    for c in content:
        c = c.get("event")
        events_list.append(str(c.get("id")))

    return events_list


if __name__ == "__main__":
    lst = events_in_group("28112")
    for i in lst:
        ev, q = event.event(i)
        print(json.dumps(ev, indent=2))
