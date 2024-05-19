import requests
import json
import headers
import datetime
import event


def events_in_group(
    group_id,
    start=datetime.datetime.now() - datetime.timedelta(days=7),
    end=datetime.datetime.now(),
):

    base_url = "https://ehms.myclub.fi/api/"
    event_url = "events/"
    full_url = base_url + event_url

    params = {"group_id": group_id, "start_date": start, "end_date": end}

    response = requests.get(full_url, headers=headers.headers, params=params)
    content = json.loads(response.content)

    events_list = []
    for c in content:
        c = c.get("event")
        #  print(c.get("id"), c.get("starts_at"), c.get("name"))
        events_list.append(str(c.get("id")))

    return events_list


if __name__ == "__main__":
    lst = events_in_group(
        "28114",
        datetime.datetime.now() - datetime.timedelta(days=30),
        datetime.datetime.now(),
    )
    for i in lst:
        llst = event.event(i)
        for ii in llst:
            print(ii)
