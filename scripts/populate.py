import csv
import requests
import os

DEBUG = True
PROD = False
URL = "https://flash-api.alabbe.fr" if PROD else "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}
PROXIES = (
    {
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080",
    }
    if DEBUG
    else {}
)


def get_profiles(parent_id=None) -> dict[str, dict]:
    url = f"{URL}/profiles/{parent_id}" if parent_id else f"{URL}/profiles"

    res = requests.get(
        url,
        headers=HEADERS,
        proxies=PROXIES,
    )

    return {profile["name"]: profile for profile in res.json()}


def get_decks(profile_id=None) -> dict[tuple[str, str], dict]:
    res = requests.get(
        f"{URL}/decks/{profile_id}",
        headers=HEADERS,
        proxies=PROXIES,
    )

    return {(deck["name"], deck["level"]): deck for deck in res.json()}


def add_profile(name, parent_id=None) -> int:
    url = f"{URL}/profile/{parent_id}" if parent_id else f"{URL}/profile"

    res = requests.post(
        url,
        json={
            "name": name,
        },
        headers=HEADERS,
        proxies=PROXIES,
    )

    if res.status_code == 201:
        return res.json()["id"]

    raise ValueError(f"Profile could not be created")


def add_deck(profile_id, name, level) -> int:
    print(f"New deck: {name} - {level}")

    res = requests.post(
        f"{URL}/deck/{profile_id}",
        json={
            "name": name,
            "level": level,
        },
        headers=HEADERS,
        proxies=PROXIES,
    )

    if res.status_code == 201:
        return res.json()["id"]

    raise ValueError(f"Deck could not be created")


def add_word(deck_id, word: dict[str, str]):
    res = requests.post(
        f"{URL}/word/{deck_id}",
        json=word,
        headers=HEADERS,
        proxies=PROXIES,
    )

    if res.status_code == 201:
        return res.json()["id"]

    raise ValueError(f"Word could not be created")


def parse_csv(path):
    current_deck = None
    decks = []

    with open(path, newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=":", quotechar='"')
        for row in spamreader:
            if row[0].strip() == "":
                decks.append(current_deck)
                current_deck = None

            elif current_deck is None:
                current_deck = {
                    "name": row[0],
                    "level": row[1],
                    "words": [],
                }

            else:
                word = {
                    "verso": row[0],
                    "recto": row[1],
                }

                if len(row) >= 3:
                    word["picture"] = row[2]

                if len(row) >= 4:
                    word["description"] = "\n".join(row[3:])

                current_deck["words"].append(word)
        decks.append(current_deck)
    return decks


def parse_data(path="data", parent_id=None):
    files = os.listdir(path)
    profiles = get_profiles(parent_id)

    if "data.csv" in files:
        decks = get_decks(parent_id)

        csv_data = parse_csv(os.path.join(path, "data.csv"))

        for csv_deck in csv_data:
            deck_name, deck_level = csv_deck["name"], csv_deck["level"]
            if (deck_name, deck_level) not in decks:
                print(
                    f"New deck: {deck_name}, level: {deck_level}, parent: {parent_id}"
                )

                deck_id = add_deck(parent_id, deck_name, deck_level)

                for word in csv_deck["words"]:
                    add_word(deck_id, word)

    for folder_name in files:
        child_path = os.path.join(path, folder_name)
        if not os.path.isdir(child_path):
            continue

        if folder_name not in profiles:
            print(f"New profile: {folder_name}, parent: {parent_id}")
            child_id = add_profile(folder_name, parent_id=parent_id)
        else:
            child_id = profiles[folder_name]["id"]

        parse_data(child_path, child_id)


parse_data()
