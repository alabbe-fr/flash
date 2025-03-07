import csv
import requests

DEBUG = True
URL = "http://127.0.0.1:5000"
HEADERS = {"Content-Type": "application/json"}
PROXIES = {"http": "http://127.0.0.1:8080"} if DEBUG else {}

with open("words.csv", newline="") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=":", quotechar='"')
    for row in spamreader:
        word = {
            "verso": row[0],
            "recto": row[1],
        }

        if len(row) >= 3:
            word["picture"] = row[2]

        if len(row) >= 4:
            word["description"] = "\n".join(row[3:])

        requests.post(
            f"{URL}/word",
            json=word,
            headers=HEADERS,
            proxies=PROXIES,
        )

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
        elif i == 1:
            j = 0
            for level in row:
                decks[j]["level"] = level
                j += 1
        else:
            j = 0
            for word in row:
                if j < len(decks):
                    decks[j]["words"].append(word)

                j += 1
        i += 1

    for deck in decks:
        requests.post(
            f"{URL}/deck",
            json=deck,
            headers=HEADERS,
            proxies=PROXIES,
        )

with open("profiles.csv", newline="") as csvfile:
    spamreader = csv.reader(csvfile, delimiter=":", quotechar='"')

    profiles = []
    i = 0

    for row in spamreader:
        if i == 0:
            for profile_name in row:
                if profile_name:
                    profiles.append(
                        {
                            "name": profile_name,
                            "decks": [],
                        }
                    )
        else:
            j = 0
            while j < len(row):
                if row[j] and row[j + 1]:
                    profiles[j // 2]["decks"].append(
                        {
                            "name": row[j],
                            "level": row[j + 1],
                        }
                    )

                j += 2
        i += 1

    for profile in profiles:
        requests.post(
            f"{URL}/profile",
            json=profile,
            headers=HEADERS,
            proxies=PROXIES,
        )
