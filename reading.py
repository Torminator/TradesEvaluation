import json
import requests
from bs4 import BeautifulSoup

with open("trades_2017.json", "r") as file:
    json_data = json.load(file)
    data = json.loads(json_data)
    print(data[0])

    r = requests.get("http://www.basketball-reference.com/" + data[0]["_Trade__team2_assets"][0]["link"])

    soup = BeautifulSoup(r.content, "html5lib")

    last_year = int(data[0]["_Trade__date"].split(",")[-1]) - 1

    contents = soup.find("tr", {"id":"per_game." + str(last_year)})
    table = contents.find_all("td")

    dict = {}
    for item in table:
        dict[item["data-stat"]] = item.contents[0]

    print(dict)