import json
import csv

with open("trades_2017_new.json", "r") as file:
    json_data = json.load(file)
    data = json.loads(json_data)

with open("trades_overview_2017.csv", "w+", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["TradeID","Date", "Team", "Inflow", "Outflow"])
    for row in data:
        t1p1 = "NA"
        t2p1 = "NA"
        if row["_Trade__inflow"]:
            if isinstance(row["_Trade__inflow"][0], dict):
                t1p1 = row["_Trade__inflow"][0]["playername"]
            else:
                t1p1 = row["_Trade__inflow"][0]

        if row["_Trade__outflow"]:
            if isinstance(row["_Trade__outflow"][0], dict):
                t2p1 =  row["_Trade__outflow"][0]["playername"]
            else:
                t2p1 = row["_Trade__outflow"][0]

        writer.writerow([row["_Trade__tradeid"],row["_Trade__date"], row["_Trade__team"], t1p1, t2p1])