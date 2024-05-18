import requests
import json


def main():

    base_url = "https://ehms.myclub.fi/api/"
    headers = {"X-myClub-token": "bb8049d99d974aa7793db6be20442d6d"}

    full_url = base_url + "groups"

    response = requests.get(full_url, headers=headers)

    content = json.loads(response.content)
    print(json.dumps(content, indent=2))


if __name__ == "__main__":
    main()
