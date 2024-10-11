import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
def categories():
    myclub_token = os.getenv("MC_TOKEN")
    headers = {"X-myClub-token": myclub_token}

    base_url = "https://ehms.myclub.fi/api/"

    full_url = base_url + "event_categories"
    response = requests.get(full_url, headers=headers)
    content = json.loads(response.content)

    categories_list = []
    # print(json.dumps(content, indent=2))
    for cat in content:
        cat = cat.get("event_category")
        category_id = cat.get("id")
        category_name = cat.get("name")
        categories_list.append(
            {"category_id": category_id, "category_name": category_name}
        )

    return categories_list


if __name__ == "__main__":
    categories()
