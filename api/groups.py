import requests
import json
import headers
import db


def get_group_ids():
    base_url = "https://ehms.myclub.fi/api/"

    full_url = base_url + "groups"
    response = requests.get(full_url, headers=headers.headers)
    content = json.loads(response.content)

    groups_list = []
    # print(json.dumps(content, indent=2))
    for c in content:
        c = c.get("group")
        group_id = c.get("id")
        group_name = c.get("name")
        groups_list.append({"group_id": group_id, "group_name": group_name})

    db.write_groups(groups_list)
    return groups_list


if __name__ == "__main__":
    get_group_ids()
