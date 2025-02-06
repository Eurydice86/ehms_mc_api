import groups
import events_in_group
import event

import datetime
import requests
import json
import os

from dotenv import load_dotenv

load_dotenv()


def upcoming_events_in_non_EHMS_venue():
    start=datetime.datetime.now().date()
    end=(start.replace(day=1) + datetime.timedelta(days=128)).replace(day=1)

    print(start, end)
    myclub_token = os.getenv("MC_TOKEN")
    headers = {"X-myClub-token": myclub_token}

    base_url = "https://ehms.myclub.fi/api/"
    event_url = "events/"
    full_url = base_url + event_url

    params = {"group_id": "28105", "venue_id": "126179", "start_date": start, "end_date": end}

    response = requests.get(full_url, headers=headers, params=params)
    content = json.loads(response.content)

    events_list = []
    for c in content:
        c = c.get("event")
        events_list.append(
            [str(c.get("id")), str(c.get("name")), str(c.get("starts_at"))]
        )

    return events_list


if __name__ == "__main__":
    lst = upcoming_events_in_non_EHMS_venue()
    print(lst)
