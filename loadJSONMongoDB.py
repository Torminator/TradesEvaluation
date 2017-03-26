from pymongo import MongoClient
import json
import csv

client = MongoClient("localhost", 27017)

db = client.trades
collection = db.trades

with open("trades_2016.json", "r") as file:
    json_data = json.load(file)
    data = json.loads(json_data)

# the grades are given in string
# want to convert them to integers
gradeConversion = {"A+": 12, "A": 11, "A-": 10, "B+": 9, "B": 8, "B-": 7, "C+": 6, "C": 5, "C-": 4,
                   "D+": 3, "D": 2, "D-": 1, "F": 0, "False": -1}

# open the csv file with the grades and read them
with open("grades_2016.csv", "r", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header = next(reader)
    grades = [gradeConversion[row[4]] for row in reader]

for idx,trade in enumerate(data):
    trade["grade"] = grades[idx]

# filter the data if the grades is set to -1 (false in the csv)
data = [row for row in data if row["grade"] != -1]

result = collection.insert_many(data)

print(result)