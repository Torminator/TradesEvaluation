import json
import requests
from bs4 import BeautifulSoup

def getPlayerStats(asset, year):
    if asset:
        if isinstance(asset, dict):
            r = requests.get("http://www.basketball-reference.com/" + asset["link"])
            soup = BeautifulSoup(r.content, "html5lib")

            contents = soup.find("tr", {"id": "per_game." + str(year)})
            if not contents:
                return  {'playername': asset['playername']}
            table = contents.find_all("td")
            if not table:
                return {'playername': asset['playername']}

            playerstats = {}
            for item in table:
                playerstats[item["data-stat"]] = item.contents[0] if item.contents else "NA"

            return {'playername': asset['playername'], 'playerstats': playerstats}

    return asset


def getAssetsWithStats(assets, last_year):
    assets_stats = []
    for asset in assets:
        assets_stats.append(getPlayerStats(asset, last_year))

    return assets_stats

if __name__ == "__main__":
    with open("trades_2017.json", "r") as file:
        json_data = json.load(file)
        data = json.loads(json_data)

        data = data[14:15]
        for trade in data:
            print(trade)
            last_year = int(trade["_Trade__date"].split(",")[-1]) - 1

            trade["_Trade__team1_assets"] = getAssetsWithStats(trade["_Trade__team1_assets"], last_year)
            trade["_Trade__team2_assets"] = getAssetsWithStats(trade["_Trade__team2_assets"], last_year)

    print(data)
    json_data = json.dumps(data)
    with open("trades_stats_2017.json", "w+") as file:
        json.dump(json_data, file)