import requests
import json
import headers
import db


def venues(start):
    base_url = "https://ehms.myclub.fi/api/"

    full_url = base_url + "venues"
    response = requests.get(full_url, headers=headers.headers)
    content = json.loads(response.content)

    venues_list = []
    for v in content:
        v = v.get("venue")
        venue_id = v.get("id")
        venue_name = v.get("name")
        city = v.get("city")
        street = v.get("street")
        map_link = v.get("map_link")
        venues_list.append(
            {
                "venue_id": venue_id,
                "venue_name": venue_name,
                "city": city,
                "street": street,
                "map_link": map_link,
            }
        )

    db.write_venues(venues_list, start)


if __name__ == "__main__":
    venues()
