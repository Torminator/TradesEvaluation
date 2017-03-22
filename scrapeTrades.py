import requests
import json
from bs4 import BeautifulSoup, element

# we store every trade made in an object of the class Trade
class  Trade:

    # the class has an attribute for the name of both teams
    # and a list of assets which they traded
    def __init__(self, team, inflow=None, outflow=None):
        self.__team = team
        if inflow is None:
            self.__inflow = []
        else:
            self.__inflow = inflow
        if outflow is None:
            self.__outflow = []
        else:
            self.__outflow = outflow
        self.__date = None
        self.__tradeid = None

    def getTeam(self):
        return self.__team

    def getInflow(self):
        return self.__inflow

    def getOutflow(self):
        return self.__outflow

    def getDate(self):
        return self.__date

    def setDate(self, date):
        self.__date = date

    def setTradeID(self, tradeid):
        self.__tradeid = tradeid

    def addInflow(self, assets):
        for asset in assets:
            self.__inflow.append(asset)

    def addOutflow(self, assets):
        for asset in assets:
            self.__outflow.append(asset)

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
            assets_1 = parseAssets(array[2:i+1])
            assets_2 = parseAssets(array[i+2:-1])
            return [Trade(array[1].contents[0], assets_2, assets_1), Trade(array[i+1].contents[0], assets_1, assets_2)]
    return []

# this function handles 3-teams trades
def parse3TeamTrade(array):
    # in a 3-team trade every transaction is listed, for example
    #   Atlanta Hawks traded Jeff Teague to the Indiana Pacers;
    # so we want to get the position of traded and to the
    # with that knowledge we know the position of the teams and the assets
    trade_index = []
    for idx,val in enumerate(array):
        if isinstance(val, str) and val.find("traded") != -1:
            start = idx
        if isinstance(val, str) and val.find("to the") != -1:
            end = idx
            trade_index.append((start, end))

    # after we got the start and end indices we need to get the idx of the teams
    # to add the assets to the correct team
    teams = []
    for index in trade_index:
        t1_idx = isCreated(array[index[0]-1].contents[0], teams)
        t2_idx = isCreated(array[index[1]+1].contents[0], teams)
        # if it is not created then we need to create it
        if t1_idx == -1:
            teams.append(Trade(array[index[0]-1].contents[0]))
            t1_idx = len(teams)-1
        # if it is not created then we need to create it
        if t2_idx == -1:
            teams.append(Trade(array[index[1]+1].contents[0]))
            t2_idx = len(teams)-1

        # get the assets with our function parseAssets
        # we use the knowledge about the position to slice the array correctly
        assets = parseAssets(array[index[0]:index[1]])

        # for the first team it loses the assets
        teams[t1_idx].addOutflow(assets)
        # and the second team receives the assets
        teams[t2_idx].addInflow(assets)

    return teams

def isCreated(teamname, teams):
    for idx, team in enumerate(teams):
        if teamname == team.getTeam():
            return idx

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
    r = requests.get("http://www.basketball-reference.com/leagues/NBA_2017_transactions.html")

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
                if deal.contents[0].find("3-team trade") != -1:
                    trade_parts = parse3TeamTrade(deal.contents)
                else:
                    trade_parts = parseTrade(deal.contents)

                if not trade_parts:
                    print("ERROR")
                else:
                    # set the date of the trade
                    for trade in trade_parts:
                        trade.setDate(date)
                        # set the id of the trade
                        trade.setTradeID("{}.{}".format(idx, trade.getDate().split(",")[-1].strip()))
                        trades.append(trade)
                        idx += 1

    # create a json string of our scraped data
    json_data = json.dumps([trade.__dict__ for trade in trades])

    # storing the data in a json file
    with  open("trades_2017_new.json", "w+") as file:
        json.dump(json_data, file)