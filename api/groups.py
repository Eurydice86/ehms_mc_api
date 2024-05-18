import requests
import json
import headers


def main():

    base_url = "https://ehms.myclub.fi/api/"

    full_url = base_url + "groups"

    response = requests.get(full_url, headers=headers.headers)

    content = json.loads(response.content)
    print(json.dumps(content, indent=2))


if __name__ == "__main__":
    main()
