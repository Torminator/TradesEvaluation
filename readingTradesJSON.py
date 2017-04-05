import json
import csv

with open("trades/trades_2013.json", "r") as file:
    json_data = json.load(file)
    data = json.loads(json_data)

with open("trades_overview_2013_new.csv", "w+", newline="") as csvfile:
    writer = csv.writer(csvfile, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Date", "Team", "Inflow", "Outflow"])
    for row in data:
        inp1 = "NA"
        outp1 = "NA"
        if row["inflow"]:
            if "player" in row["inflow"][0]:
                inp1 = row["inflow"][0]["player"]["playername"]
            else:
                inp1 = "{} round {} draft pick".format(row["inflow"][0]["draft_pick"]["round"],
                                                       row["inflow"][0]["draft_pick"]["year"])

        if row["outflow"]:
            if "player" in row["outflow"][0]:
                outp1 = row["outflow"][0]["player"]["playername"]
            else:
                outp1 = "{} round {} draft pick".format(row["outflow"][0]["draft_pick"]["round"],
                                                       row["outflow"][0]["draft_pick"]["year"])

        writer.writerow([row["date"], row["team"], inp1, outp1])