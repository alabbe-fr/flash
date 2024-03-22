import csv
import requests

URL = "http://127.0.0.1:5000"
HEADERS = {"Content-Type": "application/json"}

with open("nouns.csv", newline="") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=":", quotechar='"')
    for row in spamreader:
        noun = {
            "gender": row[0],
            "value": row[1],
            "translation": row[2],
        }

        requests.post(f"{URL}/word/noun", json=noun, headers=HEADERS)

with open("decks.csv", newline="") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=":", quotechar='"')

    decks = []
    i = 0

    for row in spamreader:
        if i == 0:
            for deck_name in row:
                decks.append(
                    {
                        "name": deck_name,
                        "words": [],
                    }
                )
        else:
            j = 0
            for word in row:
                if j < len(decks):
                    decks[j]["words"].append(word)

                j += 1
        i += 1

    for deck in decks:
        requests.post(f"{URL}/deck", json=deck, headers=HEADERS)
