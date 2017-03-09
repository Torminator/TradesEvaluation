import json
import requests
from bs4 import BeautifulSoup

# this function gets the stats for a players
# otherwise it returns the asset back
def getPlayerStats(asset, year):
    # check if asset is not empty
    if asset:
        # check if asset is of type dict because otherwise it cannot be a player
        if isinstance(asset, dict):
            # scrape basketball-reference because we saved the link in the json file
            r = requests.get("http://www.basketball-reference.com/" + asset["link"])
            soup = BeautifulSoup(r.content, "html5lib")

            # search the html for the right table
            # and check if we find them
            # if the players has played for multiple teams then there is a row called team_id = TOT
            # and it is the first one (so no problem to use contents[0])
            contents = soup.find("tr", {"id": "per_game." + str(year)})
            # if no table is found, we need to check that
            if not contents:
                return  {'playername': asset['playername']}

            table = contents.find_all("td")
            if not table:
                return {'playername': asset['playername']}

            # save the statistics in a new dict and return it
            playerstats = {}
            for item in table:
                # we want only some stats
                # filter every columns in the array out
                if item["data-stat"] not in ["team_id", "lg_id"]:
                    # check if there is an entry
                    # else we insert a 'NotAvailable'
                    if item.contents:
                        # maybe there is another html tag (like strong)
                        # so we have to get the content of that tag
                        if isinstance(item.contents[0], str):
                            playerstats[item["data-stat"]] = item.contents[0]
                        else:
                            playerstats[item["data-stat"]] = item.contents[0].contents[0]
                    else:
                        playerstats[item["data-stat"]] = "NA"

            return {'playername': asset['playername'], 'playerstats': playerstats}

    return asset

# this function just iterates over all assets in one trade for one side
# returns a new assets array with the new data
def getAssetsWithStats(assets, last_year):
    assets_stats = []
    for asset in assets:
        assets_stats.append(getPlayerStats(asset, last_year))

    return assets_stats

if __name__ == "__main__":
    # open the json file with all the trade data
    # and we parse the json
    with open("trades_2017.json", "r") as file:
        json_data = json.load(file)
        data = json.loads(json_data)

        # iterate over all trades
        size = len(data)
        for idx, trade in enumerate(data):
            # get the year for which we search the statistics for the players
            last_year = int(trade["_Trade__date"].split(",")[-1]) - 1
            # we call the function to return a new assets array with the stats for each playeer
            trade["_Trade__team1_assets"] = getAssetsWithStats(trade["_Trade__team1_assets"], last_year)
            trade["_Trade__team2_assets"] = getAssetsWithStats(trade["_Trade__team2_assets"], last_year)
            # progress info
            print("{}/{} trades completed".format(idx+1, size))

    # we save the data in a json
    json_data = json.dumps(data)
    with open("trades_stats_2017.json", "w+") as file:
        json.dump(json_data, file)