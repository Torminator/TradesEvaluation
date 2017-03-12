import requests
import json
from bs4 import BeautifulSoup, element

# we store every trade made in an object of the class Trade
class  Trade:

    # the class has an attribute for the name of both teams
    # and a list of assets which they traded
    def __init__(self, team1, team2, team1_assets, team2_assets):
        self.__tradeid = None
        self.__team1 = team1
        self.__team2 = team2
        self.__team1_assets = team1_assets
        self.__team2_assets = team2_assets
        self.__date = None

    def getTeam1(self):
        return self.__team1

    def getTeam2(self):
        return self.__team2

    def getTeam1Assets(self):
        return self.__team1_assets

    def getTeam2Assets(self):
        return self.__team2_assets

    def getDate(self):
        return self.__date

    def setDate(self, date):
        self.__date = date

    def setTradeID(self, tradeid):
        self.__tradeid = tradeid

    def __str__(self):
        return self.__team1 + " - " + self.__team2

# function gets an broken up html content
def parseTrade(array):
    # we can skip the first entry because it only contains 'the'
    for i in range(2, len(array)):
        # because every line has a typical form:
        # The <team> traded <players>, picks ... to the <team> for <players> and picks
        # we only need the index of 'to the' to partition the sentence correctly
        index = str(array[i]).find("to the")
        if index > -1:
           return Trade(array[1].contents[0], array[i+1].contents[0], parseAssets(array[2:i+1]), parseAssets(array[i+2:-1]))
    return -1

def commaAndSplitting(text):
    # we know every concatenation is either done by ',' or 'and'
    # so we split the sentence accordingly
    text_split_comma = text.split(",")
    text_split_and = text_split_comma[-1].split("and")
    if len(text_split_and) > 1:
        # if we find 'and' then we split again and the last entry of text_split_comma is now irrelevant(duplicate)
        text_split_comma.pop(-1)
        return text_split_comma + text_split_and
    else:
        return text_split_comma

def parseAssets(array):
    # these are all the fillwords used
    fillwords = [" traded ", " and ", " for ", ", ", " to the "]
    # the list to save all assets
    assets = []
    if len(array) == 1:
        # this means there is only a string
        # because players are extra entríes
        assets = commaAndSplitting(array[0][8:-8])
        # filter all cash considerations ??
        for asset in assets:
            if asset.find("cash considerations") != -1:
                assets.remove(asset)
    elif len(array) > 1:
        # again we can skip the first entry because it only states 'traded'
        for elem in array[1:]:
            # we look up if it only contains fill words
            if elem in fillwords:
                continue
            else:
                # we know a player has a <a href= > Tag
                # so we can asked if the element is a Tag
                # then the Name is saved in elem.contents[0]
                if isinstance(elem, element.Tag):
                    assets.append({"playername": elem.contents[0], "link": elem["href"]})
                else:
                    # we know it is not a player or a fillword,
                    # some the element holds information about draft picks or cash considerations
                    # we have to figure out if the string starts with an irrelevant ',' or 'and'
                    # we cut it out and use the commaAndSplitting function
                    # again we filter cash considerations
                    if elem[0] == ',':
                        start = 2
                    else:
                        start = 5
                    cash_picks = commaAndSplitting(elem[start:-8])
                    for c_p in cash_picks:
                        if c_p.find("cash considerations") != -1:
                            continue
                        assets.append(c_p)
    return assets

if __name__ == '__main__':

    # use requests to get the website
    r = requests.get("http://www.basketball-reference.com/leagues/NBA_2016_transactions.html")

    # use BeautifulSoup to parse the html
    soup = BeautifulSoup(r.content, "html5lib")

    # find the column with the data
    contents = soup.find("ul", {"class": "page_index"})
    # filter all transaction by the date
    days = contents.find_all("li")

    trades = []
    idx = 1
    for day in days:
        # find the actual date
        date = day.find("span").contents[0]
        # all transactions of a day are in <p>-Tags stored
        deals = day.find_all("p")
        for deal in deals:
            # if transaction consists of too few elements
            # it cannot be a trade
            if len(deal.contents) < 3:
                continue
            # if a coach resigns with a team then the structure of the sentence is different
            # so we have to check it
            if isinstance(deal.contents[2], element.Tag):
                continue
            # serach explicitly for the keyword 'traded'
            if deal.contents[2].find("traded") > -1:
                # call the parseTrade function and add the returning Trade object
                trade = parseTrade(deal.contents)
                if trade == -1:
                    print("ERROR")
                else:
                    # set the date of the trade
                    trade.setDate(date)
                    # set the id of the trade
                    trade.setTradeID("{}.{}".format(idx, trade.getDate().split(",")[-1].strip()))
                    trades.append(trade)
                    idx += 1

    # create a json string of our scraped data
    json_data = json.dumps([trade.__dict__ for trade in trades])

    # storing the data in a json file
    with  open("trades_2016.json", "w+") as file:
        json.dump(json_data, file)